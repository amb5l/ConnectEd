"""AI chat session — orchestrates provider tool loop and GUI driver."""

from typing import TYPE_CHECKING, Self

from PyQt6.QtCore import QObject, pyqtSignal

from ..app import settings
from ..core.check import checked

from .driver import AiDriver
from .providers import create_provider
from .types import ChatEventType, ChatMessage

if TYPE_CHECKING:
    from ..widgets.window import Window


class AiChatSession(QObject):
    userMessage    = pyqtSignal(str)
    assistantToken = pyqtSignal(str)
    toolResult     = pyqtSignal(str, str)
    error          = pyqtSignal(str)
    finished       = pyqtSignal()

    _window   : "Window"
    _driver   : AiDriver
    _provider : object
    _messages : list[ChatMessage]
    _busy     : bool

    @checked
    def __init__(self : Self, window : "Window") -> None:
        super().__init__()
        self._window = window
        self._driver = AiDriver(window)
        provider_name = settings().get("ai/provider")
        self._provider = create_provider(provider_name)
        self._messages = []
        self._busy = False

    @checked
    def isBusy(self : Self) -> bool:
        return self._busy

    @checked
    def clearHistory(self : Self) -> None:
        self._messages.clear()

    @checked
    def send(self : Self, text : str) -> None:
        text = text.strip()
        if not text or self._busy:
            return
        self._busy = True
        try:
            provider_name = settings().get("ai/provider")
            self._provider = create_provider(provider_name)
            self._messages.append(ChatMessage("user", text))
            self.userMessage.emit(text)
            max_rounds = settings().get("ai/max_tool_rounds")
            for _ in range(max_rounds):
                if not self._runProviderTurn():
                    break
        except Exception as exc:
            self.error.emit(str(exc))
        finally:
            self._busy = False
            self.finished.emit()

    def _runProviderTurn(self : Self) -> bool:
        tool_calls : list = []
        assistant_parts : list[str] = []

        for event in self._provider.chat(self._messages, self._driver.tools()):
            if event.type == ChatEventType.TOKEN:
                assistant_parts.append(event.content)
                self.assistantToken.emit(event.content)
            elif event.type == ChatEventType.TOOL_CALL:
                if event.tool_call is not None:
                    tool_calls.append(event.tool_call)
            elif event.type == ChatEventType.ERROR:
                message = event.error or event.content or "Unknown provider error"
                self.error.emit(message)
                return False
            elif event.type == ChatEventType.DONE:
                break

        if assistant_parts:
            self._messages.append(
                ChatMessage("assistant", "".join(assistant_parts))
            )

        if not tool_calls:
            return False

        for tool_call in tool_calls:
            result = self._driver.call(tool_call.name, tool_call.arguments)
            self._messages.append(
                ChatMessage(
                    "tool",
                    result,
                    tool_call_id = tool_call.id,
                    tool_name    = tool_call.name,
                )
            )
            self.toolResult.emit(tool_call.name, result)

        return True
