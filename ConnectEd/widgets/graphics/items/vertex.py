from typing import Self

from PyQt6.QtCore import QPointF

from .node import NodeItem


class VertexItem(NodeItem):
    _JUNCTION_THRESHOLD = 3

    def __init__(
        self : Self,
        pos  : QPointF | None = None
    ) -> None:
        super().__init__()
        if pos is not None:
            self.setPos(pos)
