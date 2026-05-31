"""ConnectEd GUI tools invoked by the AI agent loop."""

import json
from typing import TYPE_CHECKING, Any, Self

from ..core.check import checked

from .types import ToolDefinition

if TYPE_CHECKING:
    from ..widgets.window import Window
    from .session import AiChatSession

_PING_MESSAGE = "ConnectEd AI chat client"


class AiDriver:
    _WRITE_TOOLS : frozenset[str] = frozenset()

    _window : "Window"

    @checked
    def __init__(self : Self, window : "Window") -> None:
        self._window = window

    @checked
    def writeToolNames(self : Self) -> frozenset[str]:
        return self._WRITE_TOOLS

    @checked
    def tools(self : Self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name        = "ping",
                description = (
                    "Health check; returns the ConnectEd AI chat client identity."
                ),
                parameters  = {
                    "type"       : "object",
                    "properties" : {},
                },
            ),
        ]

    @checked
    def call(
        self       : Self,
        name       : str,
        arguments  : dict[str, Any],
        session    : "AiChatSession | None" = None,
    ) -> str:
        if name in self._WRITE_TOOLS:
            edit_lock = self._editLock()
            if edit_lock is None or edit_lock.holder() is not session:
                return json.dumps({
                    "ok"    : False,
                    "error" : "Edit lock not held by this chat",
                })

        if name == "ping":
            return self.ping()
        raise ValueError(f"Unknown AI tool: {name}")

    @checked
    def ping(self : Self) -> str:
        return _PING_MESSAGE

    def _editLock(self : Self):
        manager = self._window.aiManager()
        if manager is None:
            return None
        return manager.editLock()
