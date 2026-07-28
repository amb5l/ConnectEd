"""Narrow a mixin ``self`` to the concrete diagram view state host."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import DiagramViewState


def asDiagramViewState(obj : object) -> DiagramViewState:
    from .base import DiagramViewState
    if not isinstance(obj, DiagramViewState):
        raise TypeError("Bad host")
    return obj
