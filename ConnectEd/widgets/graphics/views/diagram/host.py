"""Narrow a mixin ``self`` to the concrete diagram view host."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import DiagramView


def asDiagramView(obj : object) -> DiagramView:
    from . import DiagramView
    if not isinstance(obj, DiagramView):
        raise TypeError("Bad host")
    return obj
