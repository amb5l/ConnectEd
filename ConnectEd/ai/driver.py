"""ConnectEd GUI tools invoked by the AI agent loop."""

import json
from typing import TYPE_CHECKING, Any, Self

from ..core.check import checked

from .types import ToolDefinition

if TYPE_CHECKING:
    from ..widgets.window import Window
    from .session import AiChatSession


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
                name        = "nobodyHome",
                description = "Stub tool for scaffolding; returns a fixed JSON payload.",
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

        if name == "nobodyHome":
            return json.dumps(self.nobodyHome())
        raise ValueError(f"Unknown AI tool: {name}")

    @checked
    def nobodyHome(self : Self) -> dict[str, Any]:
        return {
            "ok"      : True,
            "message" : "Nobody home.",
        }

    def _editLock(self : Self):
        if not hasattr(self._window, "_ai_edit_lock"):
            return None
        return self._window.aiEditLock()
