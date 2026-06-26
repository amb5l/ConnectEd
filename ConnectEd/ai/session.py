"""AI chat session — orchestrates provider tool loop and GUI driver."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from PyQt6.QtCore import QObject, Q_ARG, QMetaObject, Qt, QThread, pyqtSignal, pyqtSlot

from ..app import logger, settings
from ..core.check import checked

from .chat_worker import AiChatProviderWorker, copyMessages
from .driver import AiDriver
from .lock import AiEditLock
from .profiles import getProfile
from .prompt import buildSystemPrompt, connectionReadyMessage
from .types import ChatMessage, ToolCall

if TYPE_CHECKING:
    from ..widgets.window import Window
    from ..widgets.window.ai.chat.dock import AiChatDock


class AiChatSession(QObject):
    userMessage    = pyqtSignal(str)
    assistantToken = pyqtSignal(str)
    error          = pyqtSignal(str)
    finished       = pyqtSignal()

    _window                 : Window
    _driver                 : AiDriver
    _profile_id             : str
    _model                  : str
    _provider_name          : str
    _messages               : list[ChatMessage]
    _busy                   : bool
    _cancel_requested       : bool
    _tool_rounds_remaining  : int
    _provider_turn_active   : bool
    _thread                 : QThread
    _worker                 : AiChatProviderWorker

    @checked
    def __init__(
        self   : Self,
        window : Window,
        dock   : AiChatDock,
    ) -> None:
        super().__init__()
        self._window = window
        self._driver = AiDriver(window)
        self._profile_id = dock.profileId()
        self._model = dock.model()
        profile = getProfile(self._profile_id) if self._profile_id else None
        self._provider_name = profile.provider if profile else dock.providerKey()
        self._messages = []
        self._busy = False
        self._cancel_requested = False
        self._tool_rounds_remaining = 0
        self._provider_turn_active  = False

        self._thread = QThread()
        self._worker = AiChatProviderWorker()
        self._worker.moveToThread(self._thread)
        self._worker.token.connect(self._onWorkerToken)
        self._worker.turnFinished.connect(self._onWorkerTurnFinished)
        self._worker.providerError.connect(self._onWorkerProviderError)
        self._worker.cancelled.connect(self._onWorkerCancelled)
        self._thread.start()

        if self._isConnected():
            self._seedSystemPrompt()

    def _isConnected(self : Self) -> bool:
        return bool(self._profile_id and self._model.strip())

    def _seedSystemPrompt(self : Self) -> None:
        self._messages.append(
            ChatMessage(
                "system",
                buildSystemPrompt(
                    self._driver.tools(),
                    write_tool_names = self._driver.writeToolNames(),
                ),
            )
        )

    @checked
    def bindFromDock(self : Self, dock : AiChatDock) -> None:
        if self._busy:
            return
        self.releaseEditLock()
        self._profile_id = dock.profileId()
        self._model = dock.model()
        profile = getProfile(self._profile_id) if self._profile_id else None
        self._provider_name = profile.provider if profile else dock.providerKey()
        self._messages.clear()
        if self._isConnected():
            self._seedSystemPrompt()

    @checked
    def isBusy(self : Self) -> bool:
        return self._busy

    @checked
    def clearHistory(self : Self) -> None:
        self._messages.clear()
        if self._isConnected():
            self._seedSystemPrompt()

    @checked
    def runHandshake(self : Self) -> None:
        """Show a short ready greeting (system prompt is already seeded)."""
        if self._busy or not self._isConnected():
            return
        self._busy = True
        try:
            self.assistantToken.emit(connectionReadyMessage(self._model))
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

        if not self._isConnected():
            self.error.emit("AI chat is not connected to a model.")
            self.finished.emit()
            return

        self._busy = True
        self._cancel_requested = False
        self._tool_rounds_remaining = settings().get("ai/max_tool_rounds")
        self._messages.append(ChatMessage("user", text))
        self.userMessage.emit(text)
        self._startNextTurn()

    @checked
    def cancel(self : Self) -> None:
        if not self._busy:
            return
        self._cancel_requested = True
        if self._provider_turn_active:
            self._worker.requestCancel()
        else:
            self._finishRun()

    @checked
    def releaseEditLock(self : Self) -> None:
        edit_lock = self._editLock()
        if edit_lock is not None:
            edit_lock.release(self)

    def shutdown(self : Self) -> None:
        if self._busy:
            self.cancel()
        self._thread.quit()
        self._thread.wait(5000)

    def _editLock(self : Self) -> AiEditLock | None:
        manager = self._window.aiManager()
        if manager is None:
            return None
        return manager.editLock()

    def _startNextTurn(self : Self) -> None:
        if self._cancel_requested:
            self._finishRun()
            return
        if self._tool_rounds_remaining <= 0:
            self._finishRun()
            return
        self._tool_rounds_remaining -= 1
        messages = copyMessages(self._messages)
        tools    = list(self._driver.tools())
        self._provider_turn_active = True
        QMetaObject.invokeMethod(
            self._worker,
            "resetCancel",
            Qt.ConnectionType.QueuedConnection,
        )
        QMetaObject.invokeMethod(
            self._worker,
            "runTurn",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(str, self._profile_id),
            Q_ARG(str, self._model),
            Q_ARG(list, messages),
            Q_ARG(list, tools),
        )

    def _clearProviderTurnActive(self : Self) -> None:
        self._provider_turn_active = False

    @pyqtSlot(str)
    def _onWorkerToken(self : Self, token : str) -> None:
        if not self._cancel_requested:
            self.assistantToken.emit(token)

    @pyqtSlot(str, list)
    def _onWorkerTurnFinished(
        self            : Self,
        assistant_text  : str,
        tool_calls      : list,
    ) -> None:
        self._clearProviderTurnActive()
        if self._cancel_requested:
            self._finishRun()
            return

        calls = [tc for tc in tool_calls if isinstance(tc, ToolCall)]
        if assistant_text or calls:
            self._messages.append(
                ChatMessage(
                    "assistant",
                    assistant_text,
                    tool_calls = calls or None,
                )
            )

        if not calls:
            self._finishRun()
            return

        for tool_call in calls:
            if self._cancel_requested:
                self._finishRun()
                return
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
            logger().debug("AI tool %s: %s", tool_call.name, result)

        self._startNextTurn()

    @pyqtSlot(str)
    def _onWorkerProviderError(self : Self, message : str) -> None:
        self._clearProviderTurnActive()
        self.error.emit(message)
        self._finishRun()

    @pyqtSlot()
    def _onWorkerCancelled(self : Self) -> None:
        self._clearProviderTurnActive()
        self._finishRun()

    def _finishRun(self : Self) -> None:
        if not self._busy:
            return
        self._busy = False
        self._cancel_requested = False
        self.releaseEditLock()
        self.finished.emit()
