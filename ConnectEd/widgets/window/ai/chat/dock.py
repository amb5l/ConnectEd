from typing import TYPE_CHECKING, Self

from PyQt6.QtCore    import pyqtSignal
from PyQt6.QtWidgets import QDockWidget

from .....ai.profiles import getProfile, profileMenuLabel, providerPresetLabel

if TYPE_CHECKING:
    from ... import Window

from .widget import AiChatWidget


class AiChatDock(QDockWidget):
    chatClosed  = pyqtSignal()
    chat_widget : AiChatWidget
    _chat_id    : int
    _profile_id : str
    _provider   : str
    _model      : str

    def profileId(self : Self) -> str:
        return self._profile_id

    def providerKey(self : Self) -> str:
        return self._provider

    def model(self : Self) -> str:
        return self._model

    def isConnected(self : Self) -> bool:
        return bool(self._profile_id and self._model.strip())

    def providerLabel(self : Self) -> str:
        if not self._profile_id:
            return providerPresetLabel(self._provider)
        profile = getProfile(self._profile_id)
        if profile is not None:
            label = profileMenuLabel(profile)
            if self._model:
                return f"{label}/{self._model}"
            return label
        return providerPresetLabel(self._provider)

    def setProfileAndModel(
        self       : Self,
        profile_id : str,
        provider   : str,
        model      : str,
    ) -> None:
        self._profile_id = profile_id
        self._provider   = provider
        self._model      = model

    def __init__(
        self       : Self,
        parent     : "Window",
        chat_id    : int = 1,
        profile_id : str = "",
        provider   : str = "",
        model      : str = "",
    ) -> None:
        super().__init__(parent)
        self._chat_id = chat_id
        self._profile_id = profile_id
        self._provider = provider
        self._model = model
        self.chat_widget = AiChatWidget(parent, self)
        self.setWidget(self.chat_widget)

    def closeEvent(self : Self, event) -> None:
        self.chatClosed.emit()
        super().closeEvent(event)
