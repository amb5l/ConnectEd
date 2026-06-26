"""Window-level AI subsystem — edit lock, chat docks, profile model refresh."""

from typing import TYPE_CHECKING, Self

from PyQt6.QtCore import QObject, QTimer

from ....ai.lock import AiEditLock
from ....ai.profile_models import anyProfileMissingModels
from ....ai.profile_refresh import ProfileModelsRefreshWorker
from ....ai.profiles import loadProfiles, saveProfiles
from ....core.check import checked

from .chat import AiChatManager

if TYPE_CHECKING:
    from .. import Window
    from ..messages_view import MessagesViewDock


class AiManager(QObject):
    _window         : Window
    _edit_lock      : AiEditLock
    _chat_manager   : AiChatManager
    _refresh_worker : ProfileModelsRefreshWorker | None

    @checked
    def __init__(
        self          : Self,
        window        : Window,
        messages_dock : MessagesViewDock,
    ) -> None:
        super().__init__(window)
        self._window = window
        self._edit_lock = AiEditLock(self)
        self._chat_manager = AiChatManager(
            window,
            messages_dock,
            self._edit_lock,
        )
        menu_bar = window.menuBar()
        if menu_bar is not None:
            self._chat_manager.chatsChanged.connect(menu_bar.updateAiMenu)
        self._refresh_worker = None

    @checked
    def editLock(self : Self) -> AiEditLock:
        return self._edit_lock

    @checked
    def chatManager(self : Self) -> AiChatManager:
        return self._chat_manager

    @checked
    def scheduleStartup(self : Self) -> None:
        QTimer.singleShot(0, self.refreshProfilesIfNeeded)

    @checked
    def refreshProfilesIfNeeded(self : Self) -> None:
        profiles = loadProfiles()
        if not profiles or not anyProfileMissingModels(profiles):
            return
        worker = self._refresh_worker
        if worker is not None and worker.isRunning():
            return
        worker = ProfileModelsRefreshWorker(profiles, self._window)
        worker.finished.connect(self._onProfilesRefreshed)
        worker.start()
        self._refresh_worker = worker

    def _onProfilesRefreshed(self : Self, profiles : list) -> None:
        saveProfiles(profiles)
        menu_bar = self._window.menuBar()
        if menu_bar is not None:
            menu_bar.updateAiMenu()
        self._chat_manager.refreshChatTitles()
        self._chat_manager.refreshChatWidgets()
