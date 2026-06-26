"""ConnectEd GUI tools invoked by the AI agent loop."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Self

from ..core.check import checked

from .refs  import RefRegistry
from .tools import allToolSpecs, callTool, writeToolNames
from .types import ToolSpec

if TYPE_CHECKING:
    from ..widgets.window import Window
    from .session import AiChatSession

_PING_MESSAGE = "ConnectEd AI chat client"


class AiDriver:
    _window   : Window
    _registry : RefRegistry

    @checked
    def __init__(self : Self, window : Window) -> None:
        self._window   = window
        self._registry = RefRegistry()

    @checked
    def writeToolNames(self : Self) -> frozenset[str]:
        return writeToolNames()

    @checked
    def tools(self : Self) -> list[ToolSpec]:
        specs = list(allToolSpecs())
        specs.append(
            ToolSpec(
                name        = "ping",
                description = (
                    "Health check; returns the ConnectEd AI chat client identity."
                ),
                parameters  = {
                    "type"       : "object",
                    "properties" : {},
                },
            ),
        )
        return specs

    @checked
    def call(
        self       : Self,
        name       : str,
        arguments  : dict[str, Any],
        session    : AiChatSession | None = None,
    ) -> str:
        if name in self.writeToolNames():
            edit_lock = self._editLock()
            if edit_lock is None or edit_lock.holder() is not session:
                return json.dumps({
                    "ok"    : False,
                    "error" : "Edit lock not held by this chat",
                })

        if name == "ping":
            return self.ping()
        return callTool(name, self._window, self._registry, arguments)

    @checked
    def ping(self : Self) -> str:
        return _PING_MESSAGE

    def _editLock(self : Self):
        manager = self._window.aiManager()
        if manager is None:
            return None
        return manager.editLock()
