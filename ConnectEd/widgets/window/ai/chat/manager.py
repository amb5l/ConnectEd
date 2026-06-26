"""Manage multiple AI chat dock widgets on the main window."""

from __future__ import annotations

from typing import Self
from collections import Counter

from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtWidgets import QDockWidget

from .....ai.lock import AiEditLock
from .....core.check import checked

from .dock import AiChatDock

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ... import Window
    from ...messages_view import MessagesViewDock


def chatTitle(provider_label : str, index : int | None = None) -> str:
    title = f"AI Chat [{provider_label}]"
    if index is not None:
        title = f"{title} ({index})"
    return title


def chatTitles(provider_labels : list[str]) -> list[str]:
    counts = Counter(provider_labels)
    indices : Counter[str] = Counter()
    titles : list[str] = []
    for label in provider_labels:
        indices[label] += 1
        if counts[label] > 1:
            titles.append(chatTitle(label, indices[label]))
        else:
            titles.append(chatTitle(label))
    return titles


class AiChatManager(QObject):
    chatsChanged = pyqtSignal()

    _window        : Window
    _messages_dock : MessagesViewDock
    _edit_lock     : AiEditLock
    _chats         : list[AiChatDock]
    _next_chat_id  : int

    @checked
    def __init__(
        self          : Self,
        window        : Window,
        messages_dock : MessagesViewDock,
        edit_lock     : AiEditLock,
    ) -> None:
        super().__init__(window)
        self._window = window
        self._messages_dock = messages_dock
        self._edit_lock = edit_lock
        self._chats = []
        self._next_chat_id = 1
        self._edit_lock.lockChanged.connect(self._onEditLockChanged)

    @checked
    def chats(self : Self) -> list[AiChatDock]:
        return list(self._chats)

    @checked
    def newChat(
        self       : Self,
        profile_id : str | None = None,
        model      : str = "",
        focus      : bool = True,
    ) -> AiChatDock:
        from .....ai.chat_mru import recordChatConnection
        from .....ai.profiles import getProfile

        chat_id = self._next_chat_id
        self._next_chat_id += 1
        profile = getProfile(profile_id) if profile_id is not None else None
        if profile is not None and model.strip():
            model = model.strip()
            dock = AiChatDock(
                self._window,
                chat_id,
                profile_id = profile.id,
                provider   = profile.provider,
                model      = model,
            )
            recordChatConnection(profile.id, model)
        else:
            dock = AiChatDock(self._window, chat_id)
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
        holder = self._edit_lock.holder()
        labels = chatTitles([dock.providerLabel() for dock in self._chats])
        for dock, title in zip(self._chats, labels, strict=True):
            if holder is dock.chat_widget.session():
                title = f"{title} — Editing…"
            dock.setWindowTitle(title)

    @checked
    def refreshChatWidgets(self : Self) -> None:
        for dock in self._chats:
            dock.chat_widget.refreshWelcomeIfIdle()
            dock.chat_widget.refreshInputState()

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
        dock.chat_widget.session().shutdown()
        self._chats.remove(dock)
        dock.setParent(None)
        dock.deleteLater()
        self.refreshChatTitles()
        self.chatsChanged.emit()
