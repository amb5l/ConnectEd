"""Background worker for AI provider HTTP streaming (off the GUI thread)."""

from __future__ import annotations

from copy import deepcopy
from threading import Lock
from typing import Self

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from ..core.check import checked

from .profiles import getProfile
from .providers import createProviderForProfile
from .types import ChatEventType, ChatMessage, ToolCall, ToolSpec


def copyMessages(messages : list[ChatMessage]) -> list[ChatMessage]:
    return deepcopy(messages)


class AiChatProviderWorker(QObject):
    """Runs one provider.chat() turn on a dedicated QThread."""

    token         = pyqtSignal(str)
    turnFinished  = pyqtSignal(str, list)
    providerError = pyqtSignal(str)
    cancelled     = pyqtSignal()

    _cancel_lock : Lock
    _cancelled   : bool

    @checked
    def __init__(self : Self) -> None:
        super().__init__()
        self._cancel_lock = Lock()
        self._cancelled   = False

    @pyqtSlot()
    @checked
    def resetCancel(self : Self) -> None:
        with self._cancel_lock:
            self._cancelled = False

    @checked
    def requestCancel(self : Self) -> None:
        """Thread-safe; may be called from the GUI thread while runTurn blocks the worker."""
        with self._cancel_lock:
            self._cancelled = True

    def _isCancelled(self : Self) -> bool:
        with self._cancel_lock:
            return self._cancelled

    @pyqtSlot(str, str, list, list)
    @checked
    def runTurn(
        self       : Self,
        profile_id : str,
        model      : str,
        messages   : list[ChatMessage],
        tools      : list[ToolSpec],
    ) -> None:
        profile = getProfile(profile_id)
        if profile is None or not model.strip():
            self.providerError.emit("AI chat is not connected to a model.")
            return
        try:
            provider = createProviderForProfile(profile, model = model)
        except Exception as exc:
            self.providerError.emit(str(exc))
            return

        tool_calls      : list[ToolCall] = []
        assistant_parts : list[str]      = []

        try:
            for event in provider.chat(messages, tools):
                if self._isCancelled():
                    self.cancelled.emit()
                    return
                if event.type == ChatEventType.TOKEN:
                    assistant_parts.append(event.content)
                    self.token.emit(event.content)
                elif event.type == ChatEventType.TOOL_CALL:
                    if event.tool_call is not None:
                        tool_calls.append(event.tool_call)
                elif event.type == ChatEventType.ERROR:
                    message = event.error or event.content or "Unknown provider error"
                    self.providerError.emit(message)
                    return
                elif event.type == ChatEventType.DONE:
                    break
        except Exception as exc:
            self.providerError.emit(str(exc))
            return

        if self._isCancelled():
            self.cancelled.emit()
            return

        self.turnFinished.emit("".join(assistant_parts), tool_calls)
