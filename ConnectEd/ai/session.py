"""AI chat session — orchestrates provider tool loop and GUI driver."""

from typing import TYPE_CHECKING, Self

from PyQt6.QtCore import QObject, pyqtSignal

from ..app import settings
from ..core.check import checked

from .driver import AiDriver
from .lock import AiEditLock
from .profiles import getProfile
from .prompt import CONNECTION_HANDSHAKE_USER, buildSystemPrompt, diagramSummaryStub
from .providers import createProviderForProfile
from .types import ChatEventType, ChatMessage

if TYPE_CHECKING:
    from ..widgets.window import Window
    from ..widgets.window.ai.chat.dock import AiChatDock


class AiChatSession(QObject):
    userMessage    = pyqtSignal(str)
    assistantToken = pyqtSignal(str)
    toolResult     = pyqtSignal(str, str)
    error          = pyqtSignal(str)
    finished       = pyqtSignal()

    _window        : "Window"
    _driver        : AiDriver
    _profile_id    : str
    _model         : str
    _provider_name : str
    _provider      : object | None
    _messages      : list[ChatMessage]
    _busy          : bool

    @checked
    def __init__(
        self   : Self,
        window : "Window",
        dock   : "AiChatDock",
    ) -> None:
        super().__init__()
        self._window = window
        self._driver = AiDriver(window)
        self._profile_id = dock.profileId()
        self._model = dock.model()
        profile = getProfile(self._profile_id) if self._profile_id else None
        self._provider_name = profile.provider if profile else dock.providerKey()
        self._provider = None
        if self._profile_id and self._model.strip():
            self._provider = self._createProvider()
        self._messages = []
        self._busy = False
        if self._provider is not None:
            self._seedSystemPrompt()

    def _seedSystemPrompt(self : Self) -> None:
        self._messages.append(
            ChatMessage(
                "system",
                buildSystemPrompt(
                    self._driver.tools(),
                    diagramSummaryStub(),
                    write_tool_names = self._driver.writeToolNames(),
                ),
            )
        )

    def _createProvider(self : Self) -> object:
        profile = getProfile(self._profile_id) if self._profile_id else None
        if profile is None or not self._model.strip():
            raise ValueError("AI chat is not connected to a model.")
        return createProviderForProfile(profile, model = self._model)

    @checked
    def bindFromDock(self : Self, dock : "AiChatDock") -> None:
        if self._busy:
            return
        self.releaseEditLock()
        self._profile_id = dock.profileId()
        self._model = dock.model()
        profile = getProfile(self._profile_id) if self._profile_id else None
        self._provider_name = profile.provider if profile else dock.providerKey()
        self._provider = self._createProvider()
        self._messages.clear()
        self._seedSystemPrompt()

    @checked
    def isBusy(self : Self) -> bool:
        return self._busy

    @checked
    def clearHistory(self : Self) -> None:
        self._messages.clear()
        if self._provider is not None:
            self._seedSystemPrompt()

    @checked
    def runHandshake(self : Self) -> None:
        """Deliver the system prompt to the model and show a ready greeting."""
        if self._busy or self._provider is None:
            return
        self._busy = True
        try:
            self._provider = self._createProvider()
            self._messages.append(
                ChatMessage("user", CONNECTION_HANDSHAKE_USER),
            )
            assistant_parts : list[str] = []
            for event in self._provider.chat(self._messages, []):
                if event.type == ChatEventType.TOKEN:
                    assistant_parts.append(event.content)
                    self.assistantToken.emit(event.content)
                elif event.type == ChatEventType.TOOL_CALL:
                    pass
                elif event.type == ChatEventType.ERROR:
                    message = event.error or event.content or "Unknown provider error"
                    self.error.emit(message)
                    return
                elif event.type == ChatEventType.DONE:
                    break
            text = "".join(assistant_parts).strip()
            if not text:
                self.error.emit("No response from model on connect.")
                return
            self._messages.append(ChatMessage("assistant", text))
        except Exception as exc:
            self.error.emit(str(exc))
        finally:
            self._busy = False
            self.finished.emit()

    @checked
    def send(self : Self, text : str) -> None:
        text = text.strip()
        if not text or self._busy:
            return

        edit_lock = self._editLock()
        if edit_lock is not None and not edit_lock.acquire(self):
            self.error.emit("Another AI chat is editing the diagram.")
            self.finished.emit()
            return

        self._busy = True
        try:
            self._provider = self._createProvider()
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
            if edit_lock is not None:
                edit_lock.release(self)
            self.finished.emit()

    @checked
    def releaseEditLock(self : Self) -> None:
        edit_lock = self._editLock()
        if edit_lock is not None:
            edit_lock.release(self)

    def _editLock(self : Self) -> AiEditLock | None:
        manager = self._window.aiManager()
        if manager is None:
            return None
        return manager.editLock()

    def _runProviderTurn(self : Self) -> bool:
        if self._provider is None:
            raise ValueError("AI chat is not connected to a model.")
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

        if assistant_parts or tool_calls:
            self._messages.append(
                ChatMessage(
                    "assistant",
                    "".join(assistant_parts),
                    tool_calls = tool_calls or None,
                )
            )

        if not tool_calls:
            return False

        for tool_call in tool_calls:
            result = self._driver.call(
                tool_call.name,
                tool_call.arguments,
                session = self,
            )
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
