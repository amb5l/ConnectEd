"""ConnectEd GUI tools invoked by the AI agent loop."""

import json
from typing import TYPE_CHECKING, Any, Self

from ..core.check import checked

from .types import ToolDefinition

if TYPE_CHECKING:
    from ..widgets.window import Window


class AiDriver:
    _window : "Window"

    @checked
    def __init__(self : Self, window : "Window") -> None:
        self._window = window

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
    def call(self : Self, name : str, arguments : dict[str, Any]) -> str:
        if name == "nobodyHome":
            return json.dumps(self.nobodyHome())
        raise ValueError(f"Unknown AI tool: {name}")

    @checked
    def nobodyHome(self : Self) -> dict[str, Any]:
        return {
            "ok"      : True,
            "message" : "Nobody home.",
        }
