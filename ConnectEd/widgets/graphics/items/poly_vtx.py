from typing import Self

from PyQt6.QtCore import QPointF

from .handle import Handle

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .mixin.vertex import ItemVertexMixin


class PolyVtx(Handle):
    _PATH_NAME = "PolyVtx"
    def __init__(
        self   : Self,
        parent : "ItemVertexMixin",
        pos    : QPointF | None = None
    ) -> None:
        super().__init__(parent, pos)

    def moveBy(self : Self, delta : QPointF) -> None:
        self.setPos(self.pos() + delta)
        parent : "ItemVertexMixin" = self.parentItem()
        parent.updateVertices()
