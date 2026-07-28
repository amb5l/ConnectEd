"""Narrow a mixin ``self`` to the concrete diagram scene host."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import DiagramScene


def asDiagramScene(obj : object) -> DiagramScene:
    from . import DiagramScene
    if not isinstance(obj, DiagramScene):
        raise TypeError("Bad host")
    return obj
