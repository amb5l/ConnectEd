from typing import TYPE_CHECKING, Self

from PyQt6.QtWidgets import QDockWidget

from ....app import settings

if TYPE_CHECKING:
    from .. import Window

from .widget import AiChatWidget


class AiChatDock(QDockWidget):
    WINDOW_TITLE = "AI Chat"

    chat_widget : AiChatWidget

    @staticmethod
    def providerLabel() -> str:
        provider = settings().get("ai/provider")
        if provider and provider != "dummy":
            return str(provider)
        return "no provider"

    def refreshTitle(self : Self) -> None:
        self.setWindowTitle(f"{self.WINDOW_TITLE} - [{self.providerLabel()}]")

    def __init__(self : Self, parent : "Window") -> None:
        super().__init__(parent)
        self.chat_widget = AiChatWidget(parent, self)
        self.setWidget(self.chat_widget)
        self.refreshTitle()
