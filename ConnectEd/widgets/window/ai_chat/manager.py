"""Manage multiple AI chat dock widgets on the main window."""

from collections import Counter
from typing import TYPE_CHECKING, Self

from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtWidgets import QDockWidget

from ....core.check import checked

from .dock import AiChatDock

if TYPE_CHECKING:
    from .. import Window
    from ..messages_view import MessagesViewDock


def chatTitles(provider_labels : list[str]) -> list[str]:
    counts = Counter(provider_labels)
    indices : Counter[str] = Counter()
    titles : list[str] = []
    for label in provider_labels:
        indices[label] += 1
        if counts[label] > 1:
            titles.append(f"{label} ({indices[label]})")
        else:
            titles.append(label)
    return titles


class AiChatManager(QObject):
    chatsChanged = pyqtSignal()

    _window        : "Window"
    _messages_dock : "MessagesViewDock"
    _chats         : list[AiChatDock]
    _next_chat_id  : int

    @checked
    def __init__(
        self       : Self,
        window     : "Window",
        messages_dock : "MessagesViewDock",
    ) -> None:
        super().__init__(window)
        self._window = window
        self._messages_dock = messages_dock
        self._chats = []
        self._next_chat_id = 1
        edit_lock = window.aiEditLock()
        if edit_lock is not None:
            edit_lock.lockChanged.connect(self._onEditLockChanged)

    @checked
    def chats(self : Self) -> list[AiChatDock]:
        return list(self._chats)

    @checked
    def newChat(
        self      : Self,
        provider  : str | None = None,
        focus     : bool = True,
    ) -> AiChatDock:
        from ....app import settings

        chat_id = self._next_chat_id
        self._next_chat_id += 1
        provider_key = provider or settings().get("ai/provider")
        dock = AiChatDock(self._window, chat_id, provider_key)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )
        dock.chatClosed.connect(lambda d=dock : self._onChatClosed(d))

        qd = Qt.DockWidgetArea
        if not self._chats:
            self._window.addDockWidget(qd.BottomDockWidgetArea, dock)
            self._window.splitDockWidget(
                self._messages_dock,
                dock,
                Qt.Orientation.Horizontal,
            )
        else:
            self._window.addDockWidget(qd.BottomDockWidgetArea, dock)
            self._window.tabifyDockWidget(self._chats[0], dock)

        self._chats.append(dock)
        self.refreshChatTitles()
        if focus:
            self.focusChat(dock)
        self.chatsChanged.emit()
        return dock

    @checked
    def refreshChatTitles(self : Self) -> None:
        edit_lock = self._window.aiEditLock()
        holder = edit_lock.holder() if edit_lock is not None else None
        labels = chatTitles([dock.providerLabel() for dock in self._chats])
        for dock, title in zip(self._chats, labels, strict=True):
            if holder is dock.chat_widget.session():
                title = f"{title} — Editing…"
            dock.setWindowTitle(title)

    @checked
    def refreshChatWidgets(self : Self) -> None:
        for dock in self._chats:
            dock.chat_widget.refreshSendState()

    def _onEditLockChanged(self : Self) -> None:
        self.refreshChatTitles()
        self.refreshChatWidgets()

    @checked
    def focusChat(self : Self, dock : AiChatDock) -> None:
        dock.show()
        dock.raise_()

    def _onChatClosed(self : Self, dock : AiChatDock) -> None:
        if dock not in self._chats:
            return
        dock.chat_widget.releaseEditLock()
        self._chats.remove(dock)
        dock.setParent(None)
        dock.deleteLater()
        self.refreshChatTitles()
        self.chatsChanged.emit()
