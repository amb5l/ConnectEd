from typing import TYPE_CHECKING, Self

from PyQt6.QtCore    import pyqtSignal
from PyQt6.QtWidgets import QDockWidget

from ....ai.providers import providerDisplayLabel

if TYPE_CHECKING:
    from .. import Window

from .widget import AiChatWidget


class AiChatDock(QDockWidget):
    chatClosed  = pyqtSignal()
    chat_widget : AiChatWidget
    _chat_id    : int
    _provider   : str

    def providerKey(self : Self) -> str:
        return self._provider

    def providerLabel(self : Self) -> str:
        return providerDisplayLabel(self._provider)

    def __init__(
        self       : Self,
        parent     : "Window",
        chat_id    : int = 1,
        provider   : str = "dummy",
    ) -> None:
        super().__init__(parent)
        self._chat_id = chat_id
        self._provider = provider
        self.chat_widget = AiChatWidget(parent, self)
        self.setWidget(self.chat_widget)

    def closeEvent(self : Self, event) -> None:
        self.chatClosed.emit()
        super().closeEvent(event)
