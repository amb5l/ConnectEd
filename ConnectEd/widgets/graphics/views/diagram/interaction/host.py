"""Narrow a mixin ``self`` to the concrete diagram interaction host."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from . import DiagramInteraction, DiagramItemInteraction


def asDiagramInteraction(obj : object) -> DiagramInteraction:
    from . import DiagramInteraction
    if not isinstance(obj, DiagramInteraction):
        raise TypeError("Bad host")
    return obj


def asDiagramItemInteraction(obj : object) -> DiagramItemInteraction[Any]:
    from . import DiagramItemInteraction
    if not isinstance(obj, DiagramItemInteraction):
        raise TypeError("Bad host")
    return obj
