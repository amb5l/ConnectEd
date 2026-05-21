from typing import TYPE_CHECKING, Self

from PyQt6.QtCore    import Qt, QUrl
from PyQt6.QtGui     import QDesktopServices
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from ....ai.html import escape, linkify
from ....ai.session import AiChatSession
from ....ai.welcome import welcomeHtml
from ....widgets.dialogs.ai_settings import AiSettingsDialog

if TYPE_CHECKING:
    from .. import Window

    from . import AiChatDock


class AiChatWidget(QWidget):
    _window                 : "Window"
    _dock                   : "AiChatDock"
    _session                : AiChatSession
    _history                : QTextBrowser
    _input                  : QLineEdit
    _send                   : QPushButton
    _assistant_line_open    : bool
    _assistant_stream_plain : bool

    def __init__(self : Self, window : "Window", dock : "AiChatDock") -> None:
        super().__init__(window)
        self._window = window
        self._dock = dock
        self._session = AiChatSession(window)
        self._session.userMessage.connect(self._onUserMessage)
        self._session.assistantToken.connect(self._onAssistantToken)
        self._session.toolResult.connect(self._onToolResult)
        self._session.error.connect(self._onError)
        self._session.finished.connect(self._onFinished)
        self._assistant_line_open = False
        self._assistant_stream_plain = False

        self._history = QTextBrowser(self)
        self._history.setReadOnly(True)
        self._history.setOpenExternalLinks(False)
        self._history.anchorClicked.connect(self._onAnchorClicked)
        self._history.setPlaceholderText("AI chat history")

        self._input = QLineEdit(self)
        self._input.setPlaceholderText("Message…")
        self._input.returnPressed.connect(self._sendMessage)

        self._send = QPushButton("Send", self)
        self._send.clicked.connect(self._sendMessage)

        input_row = QHBoxLayout()
        input_row.addWidget(self._input, 1)
        input_row.addWidget(self._send)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.addWidget(self._history, 1)
        layout.addLayout(input_row)

        self._appendRichBlock("Assistant", welcomeHtml())

    def _refreshTitle(self : Self) -> None:
        self._dock.refreshTitle()

    def _scrollHistory(self : Self) -> None:
        bar = self._history.verticalScrollBar()
        bar.setValue(bar.maximum())

    def _appendRichBlock(self : Self, role : str, html_body : str) -> None:
        cursor = self._history.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertHtml(f"<p><b>{escape(role)}</b></p>{html_body}")
        self._scrollHistory()

    def _appendPlainBlock(self : Self, role : str, text : str) -> None:
        cursor = self._history.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertHtml(f"<p><b>{escape(role)}:</b> {linkify(text)}</p>")
        self._scrollHistory()

    def _onAnchorClicked(self : Self, url : QUrl) -> None:
        if url.scheme() == "connected":
            if url.host() == "ai" and url.path() in ("/settings", "settings"):
                self._openAiSettings()
            return
        if url.scheme() in ("https", "http"):
            QDesktopServices.openUrl(url)

    def _openAiSettings(self : Self) -> None:
        dialog = AiSettingsDialog(self._window)
        if dialog.exec():
            self._refreshTitle()

    def _sendMessage(self : Self) -> None:
        text = self._input.text()
        if not text.strip() or self._session.isBusy():
            return
        self._input.clear()
        self._assistant_line_open = False
        self._assistant_stream_plain = False
        self._send.setEnabled(False)
        self._session.send(text)

    def _onUserMessage(self : Self, text : str) -> None:
        self._appendPlainBlock("You", text)

    def _onAssistantToken(self : Self, token : str) -> None:
        cursor = self._history.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        if not self._assistant_line_open:
            cursor.insertHtml("<p><b>Assistant:</b> ")
            self._assistant_line_open = True
            self._assistant_stream_plain = True
        if self._assistant_stream_plain:
            cursor.insertText(token)
        self._scrollHistory()

    def _onToolResult(self : Self, name : str, result : str) -> None:
        self._assistant_line_open = False
        self._assistant_stream_plain = False
        cursor = self._history.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertHtml(
            f"<p><b>{escape(f'Tool [{name}]')}:</b></p>"
            f"<pre>{escape(result)}</pre>"
        )
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
        self._send.setEnabled(True)
        self._input.setFocus(Qt.FocusReason.OtherFocusReason)
