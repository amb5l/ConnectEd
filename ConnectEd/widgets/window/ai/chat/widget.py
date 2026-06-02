from typing import TYPE_CHECKING, Self

from PyQt6.QtCore    import QEvent, QObject, Qt, QTimer, QUrl
from PyQt6.QtGui     import (
    QDesktopServices,
    QFont,
    QKeySequence,
    QPalette,
    QShortcut,
    QTextCharFormat,
    QTextCursor,
    QWheelEvent,
)
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from .....app import settings

from .....ai.chat_mru import recordChatConnection
from .....ai.html     import escape, historyStyleSheet, linkify, userMessageHtml
from .....ai.session  import AiChatSession
from .....ai.welcome  import parseChatLink, welcomeHtml

from ....dialogs.ai_profiles import AiProfilesDialog

if TYPE_CHECKING:
    from ... import Window

    from .dock import AiChatDock

_CONNECTED_PLACEHOLDER    = "Message…"
_DISCONNECTED_PLACEHOLDER = "disconnected"
_INPUT_DISCONNECTED_STYLE = (
    "QLineEdit:disabled { font-style: italic; }"
    "QLineEdit:disabled::placeholder { font-style: italic; }"
)
_USER_BUBBLE_LIGHTER = 115
_CHAT_FONT_SIZE_MIN  = 6
_CHAT_FONT_SIZE_MAX  = 24


class _AiChatFontZoomHost:
    """Shared font-zoom API for history and input sub-widgets."""

    _font_size : int

    def _chatFont(self : Self) -> QFont:
        font = QFont()
        font.setPointSizeF(self._font_size)
        return font

    def _increaseChatFontSize(self : Self) -> None:
        self._font_size = min(self._font_size + 1, _CHAT_FONT_SIZE_MAX)
        self._applyChatFontSize()

    def _decreaseChatFontSize(self : Self) -> None:
        self._font_size = max(self._font_size - 1, _CHAT_FONT_SIZE_MIN)
        self._applyChatFontSize()

    def _applyChatFontSize(self : Self) -> None:
        font = self._chatFont()
        self._history.setFont(font)
        self._history.document().setDefaultFont(font)
        self._input.setFont(font)
        self._rescaleHistoryDocumentFont()

    def _rescaleHistoryDocumentFont(self : Self) -> None:
        cursor = QTextCursor(self._history.document())
        cursor.beginEditBlock()
        cursor.select(QTextCursor.SelectionType.Document)
        fmt = QTextCharFormat()
        fmt.setFontPointSize(self._font_size)
        cursor.mergeCharFormat(fmt)
        cursor.clearSelection()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.endEditBlock()
        self._history.setTextCursor(cursor)


class AiChatHistoryBrowser(QTextBrowser):
    _zoom_host : _AiChatFontZoomHost

    def __init__(
        self   : Self,
        host   : _AiChatFontZoomHost,
        parent : QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._zoom_host = host
        self.viewport().installEventFilter(self)

    def eventFilter(self : Self, watched : QObject, event : QEvent) -> bool:
        if (
            watched is self.viewport()
            and event.type() == QEvent.Type.Wheel
        ):
            wheel = event
            if wheel.modifiers() & Qt.KeyboardModifier.ControlModifier:
                delta = wheel.angleDelta().y()
                if delta > 0:
                    self._zoom_host._increaseChatFontSize()
                elif delta < 0:
                    self._zoom_host._decreaseChatFontSize()
                wheel.accept()
                return True
        return super().eventFilter(watched, event)

    def wheelEvent(self : Self, event : QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self._zoom_host._increaseChatFontSize()
            elif delta < 0:
                self._zoom_host._decreaseChatFontSize()
            event.accept()
            return
        super().wheelEvent(event)


class AiChatLineEdit(QLineEdit):
    _zoom_host : _AiChatFontZoomHost

    def __init__(
        self   : Self,
        host   : _AiChatFontZoomHost,
        parent : QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._zoom_host = host

    def wheelEvent(self : Self, event : QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self._zoom_host._increaseChatFontSize()
            elif delta < 0:
                self._zoom_host._decreaseChatFontSize()
            event.accept()
            return
        super().wheelEvent(event)


class AiChatWidget(QWidget, _AiChatFontZoomHost):
    _window                 : "Window"
    _dock                   : "AiChatDock"
    _session                : AiChatSession
    _history                : QTextBrowser
    _input                  : QLineEdit
    _send                   : QPushButton
    _stop                   : QPushButton
    _assistant_line_open    : bool
    _assistant_stream_plain : bool
    _pin_welcome_top        : bool
    _font_size              : int

    def __init__(self : Self, window : "Window", dock : "AiChatDock") -> None:
        super().__init__(window)
        self._window = window
        self._dock = dock
        self._session = AiChatSession(window, dock)
        self._session.userMessage.connect(self._onUserMessage)
        self._session.assistantToken.connect(self._onAssistantToken)
        self._session.error.connect(self._onError)
        self._session.finished.connect(self._onFinished)
        self._assistant_line_open = False
        self._assistant_stream_plain = False
        self._pin_welcome_top = True
        self._font_size = int(settings().get("display/font_size"))

        ai_manager = window.aiManager()
        edit_lock = ai_manager.editLock() if ai_manager is not None else None
        if edit_lock is not None:
            edit_lock.lockChanged.connect(self.refreshSendState)

        self._history = AiChatHistoryBrowser(self, self)
        self._history.setReadOnly(True)
        self._history.setOpenExternalLinks(False)
        self._refreshHistoryStyle()
        self._history.anchorClicked.connect(self._onAnchorClicked)
        self._history.setPlaceholderText("AI chat history")

        self._input = AiChatLineEdit(self, self)
        self._input.setPlaceholderText(_CONNECTED_PLACEHOLDER)
        self._input.returnPressed.connect(self._sendMessage)
        palette = self._input.palette()
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.PlaceholderText,
            palette.color(QPalette.ColorRole.PlaceholderText),
        )
        self._input.setPalette(palette)

        self._send = QPushButton("Send", self)
        self._send.clicked.connect(self._sendMessage)

        self._stop = QPushButton("Stop", self)
        self._stop.setEnabled(False)
        self._stop.clicked.connect(self._stopMessage)

        input_row = QHBoxLayout()
        input_row.addWidget(self._input, 1)
        input_row.addWidget(self._send)
        input_row.addWidget(self._stop)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.addWidget(self._history, 1)
        layout.addLayout(input_row)

        self._applyChatFontSize()
        shortcut_ctx = Qt.ShortcutContext.WidgetWithChildrenShortcut
        for sequence in ("Ctrl+=", "Ctrl++"):
            increase_font = QShortcut(QKeySequence(sequence), self)
            increase_font.setContext(shortcut_ctx)
            increase_font.activated.connect(self._increaseChatFontSize)
        decrease_font = QShortcut(QKeySequence("Ctrl+-"), self)
        decrease_font.setContext(shortcut_ctx)
        decrease_font.activated.connect(self._decreaseChatFontSize)

        self._showWelcome()
        self.refreshInputState()

    def showEvent(self : Self, event) -> None:
        super().showEvent(event)
        if self._pin_welcome_top:
            self._scheduleScrollToTop()

    def session(self : Self) -> AiChatSession:
        return self._session

    def releaseEditLock(self : Self) -> None:
        self._session.releaseEditLock()

    def refreshInputState(self : Self) -> None:
        connected = self._dock.isConnected()
        if connected:
            self._input.setEnabled(True)
            self._input.setPlaceholderText(_CONNECTED_PLACEHOLDER)
            self._input.setStyleSheet("")
        else:
            self._input.clear()
            self._input.setEnabled(False)
            self._input.setPlaceholderText(_DISCONNECTED_PLACEHOLDER)
            self._input.setStyleSheet(_INPUT_DISCONNECTED_STYLE)
        self.refreshSendState()

    def refreshSendState(self : Self) -> None:
        can_send = self._canSend()
        busy     = self._session.isBusy()
        self._send.setEnabled(can_send)
        self._stop.setEnabled(busy and self._dock.isConnected())
        if can_send:
            self._send.setToolTip("")
            return
        edit_lock = self._editLock()
        if (
            edit_lock is not None
            and edit_lock.isLocked()
            and edit_lock.holder() is not self._session
        ):
            self._send.setToolTip("Another AI chat is editing the diagram.")
        elif busy:
            self._send.setToolTip("")
        else:
            self._send.setToolTip("")

    def _editLock(self : Self):
        ai_manager = self._window.aiManager()
        if ai_manager is None:
            return None
        return ai_manager.editLock()

    def _canSend(self : Self) -> bool:
        if not self._dock.isConnected():
            return False
        if self._session.isBusy():
            return False
        edit_lock = self._editLock()
        if edit_lock is not None and edit_lock.isLocked():
            return edit_lock.holder() is self._session
        return True

    def refreshWelcomeIfIdle(self : Self) -> None:
        """Refresh the welcome message when the user has not started chatting."""
        if not self._pin_welcome_top:
            return
        self._showWelcome()

    def bindChat(self : Self, profile_id : str, model : str) -> None:
        from .....ai.profiles import getProfile

        profile = getProfile(profile_id)
        if profile is None or not model:
            return
        self._dock.setProfileAndModel(profile_id, profile.provider, model)
        try:
            self._session.bindFromDock(self._dock)
        except Exception as exc:
            self._appendPlainBlock("Error", str(exc))
            return
        self._pin_welcome_top = False
        self._assistant_line_open = False
        self._assistant_stream_plain = False
        self._history.clear()
        recordChatConnection(profile_id, model)
        self.refreshSendState()
        self._session.runHandshake()
        manager = self._window.aiChatManager()
        if manager is not None:
            manager.refreshChatTitles()
        self.refreshInputState()
        self._input.setFocus(Qt.FocusReason.OtherFocusReason)

    def _scrollHistory(self : Self, *, top : bool = False) -> None:
        if top:
            self._scheduleScrollToTop()
            return
        bar = self._history.verticalScrollBar()
        bar.setValue(bar.maximum())

    def _scrollToTop(self : Self) -> None:
        cursor = self._history.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        self._history.setTextCursor(cursor)
        self._history.verticalScrollBar().setValue(0)

    def _scheduleScrollToTop(self : Self) -> None:
        self._scrollToTop()
        QTimer.singleShot(0, self._scrollToTop)

    def _showWelcome(self : Self) -> None:
        self._requestModelRefreshIfNeeded()
        self._history.setHtml(welcomeHtml())
        self._rescaleHistoryDocumentFont()
        self._scheduleScrollToTop()

    def _requestModelRefreshIfNeeded(self : Self) -> None:
        from .....ai.profile_models import anyProfileMissingModels
        from .....ai.profiles import loadProfiles

        profiles = loadProfiles()
        if not profiles or not anyProfileMissingModels(profiles):
            return
        ai_manager = self._window.aiManager()
        if ai_manager is not None:
            ai_manager.refreshProfilesIfNeeded()

    def _appendHtmlAtEnd(self : Self, html : str) -> None:
        cursor = self._history.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        if cursor.position() > 0 and cursor.block().length() > 1:
            cursor.insertBlock()
        cursor.setCharFormat(self._historyBodyCharFormat())
        cursor.insertHtml(html)
        self._scrollHistory()

    def _refreshHistoryStyle(self : Self) -> None:
        self._history.document().setDefaultStyleSheet(historyStyleSheet())

    def _historyBodyCharFormat(self : Self) -> QTextCharFormat:
        """Plain body text — avoids inheriting link/bold/pre from prior HTML."""
        fmt = QTextCharFormat()
        fmt.setFont(self._chatFont())
        fmt.setFontWeight(QFont.Weight.Normal)
        fmt.setFontItalic(False)
        fmt.setFontUnderline(False)
        fmt.setForeground(self._history.palette().color(QPalette.ColorRole.Text))
        return fmt

    def _userBubbleColor(self : Self) -> str:
        base = self._history.palette().color(QPalette.ColorRole.Base)
        return base.lighter(_USER_BUBBLE_LIGHTER).name()

    def _appendUserMessage(self : Self, text : str) -> None:
        self._appendHtmlAtEnd(userMessageHtml(text, self._userBubbleColor()))

    def _appendPlainBlock(self : Self, role : str, text : str) -> None:
        self._appendHtmlAtEnd(
            f"<p><b>{escape(role)}:</b> {linkify(text)}</p>",
        )

    def _onAnchorClicked(self : Self, url : QUrl) -> None:
        if url.scheme() == "connected":
            if url.host() == "ai" and url.path() in ("/settings", "settings"):
                self._openAiSettings()
                return
            link = parseChatLink(url.toString())
            if link is not None:
                profile_id, model = link
                self.bindChat(profile_id, model)
            return
        if url.scheme() in ("https", "http"):
            QDesktopServices.openUrl(url)

    def _openAiSettings(self : Self) -> None:
        dialog = AiProfilesDialog(self._window)
        if not dialog.exec():
            return
        manager = self._window.aiChatManager()
        if manager is None:
            return
        manager.refreshChatTitles()
        manager.refreshChatWidgets()
        self._window.menuBar().updateAiMenu()

    def _stopMessage(self : Self) -> None:
        self._session.cancel()

    def _sendMessage(self : Self) -> None:
        text = self._input.text()
        if not text.strip() or not self._canSend():
            return
        if self._dock.isConnected():
            recordChatConnection(self._dock.profileId(), self._dock.model())
        self._pin_welcome_top = False
        self._input.clear()
        self._assistant_line_open = False
        self._assistant_stream_plain = False
        self.refreshSendState()
        self._session.send(text)

    def _onUserMessage(self : Self, text : str) -> None:
        self._appendUserMessage(text)

    def _onAssistantToken(self : Self, token : str) -> None:
        cursor = self._history.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        body_fmt = self._historyBodyCharFormat()
        if not self._assistant_line_open:
            if cursor.position() > 0 and cursor.block().length() > 1:
                cursor.insertBlock()
            cursor.setCharFormat(body_fmt)
            cursor.insertHtml("<p>")
            cursor.setCharFormat(body_fmt)
            self._assistant_line_open = True
            self._assistant_stream_plain = True
        if self._assistant_stream_plain:
            cursor.setCharFormat(body_fmt)
            cursor.insertText(token)
        self._history.setTextCursor(cursor)
        self._scrollHistory()

    def _onError(self : Self, message : str) -> None:
        self._assistant_line_open = False
        self._assistant_stream_plain = False
        self._appendPlainBlock("Error", message)

    def _onFinished(self : Self) -> None:
        if self._assistant_line_open and self._assistant_stream_plain:
            cursor = self._history.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            cursor.insertHtml("</p>")
        self._assistant_line_open = False
        self._assistant_stream_plain = False
        self.refreshSendState()
        self.refreshInputState()
        self._input.setFocus(Qt.FocusReason.OtherFocusReason)
