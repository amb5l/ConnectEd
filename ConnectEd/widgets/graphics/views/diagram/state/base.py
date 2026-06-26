from __future__ import annotations

from ...drawing.state.base import DrawingViewStateBase, qkm

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DiagramView
    from ....scenes.diagram import DiagramScene


class DiagramViewStateBase(DrawingViewStateBase):
    # instance attributes
    view   : DiagramView
    scene  : DiagramScene


__all__ = ["DiagramViewStateBase", "qkm"]
