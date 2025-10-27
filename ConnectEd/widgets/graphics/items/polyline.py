from typing import Self, overload

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtGui     import QPainterPath

from .base_rect import BaseRectangleMixin

from .mixin        import ItemMixin
from .mixin.pos    import ItemPosMixin
from .mixin.paint  import ItemPaintMixin
from .mixin.vertex import ItemVertexMixin
from .mixin.anchor import ItemRectAnchorPointsMixin
from .mixin.line   import ItemLineMixin
from .mixin.change import ItemChangeMixin
from .mixin.clone  import ItemCloneMixin
from .mixin.xml    import ItemXmlMixin
from .mixin.menu   import ItemMenuMixin


class Polyline(
    ItemMixin,
    ItemPosMixin,
    ItemPaintMixin,
    ItemVertexMixin,
    ItemRectAnchorPointsMixin,
    ItemLineMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    QGraphicsPathItem
):
    def __init__(self : Self, pos : QPointF) -> None:
        super().__init__()
        self.initItem()
        self.setPos(pos)
        self.updateVertices()

    def anchorPointRect(self : Self) -> QRectF:
        return self.path().controlPointRect()

    def updateVertices(self : Self) -> None:
        path = QPainterPath()
        path.moveTo(self._vertices[0].pos())
        for vertex in self._vertices[1:]:
            path.lineTo(vertex.pos())
        self.setPath(path)
        self.updateAnchorPoints()

    def rect(self : Self) -> QRectF:
        return self.boundingRect()

    @overload
    def setPoints(
        self : Self,
        p1   : QPointF,
        p2   : QPointF
    ) -> None:
        ...

    @overload
    def setPoints(
        self : Self,
        x1   : float | int,
        y1   : float | int,
        x2   : float | int,
        y2   : float | int
    ) -> None:
        ...

    def setPoints(
        self : Self,
        p1_x1 : QPointF | float | int,
        p2_y1 : QPointF | float | int,
        x2    : float | int | None = None,
        y2    : float | int | None = None
    ) -> None:
        if x2 is None or y2 is None:
            x1 = p1_x1.x()
            y1 = p1_x1.y()
            x2 = p2_y1.x()
            y2 = p2_y1.y()
        else:
            x1 = p1_x1
            y1 = p2_y1
        final_pos = QPointF(
            x1 if x1 < x2 else x2,
            y1 if y1 < y2 else y2,
        )
        self.setPos(final_pos)
        scale_x = abs(x2-x1) / self.rect().width()
        scale_y = abs(y2-y1) / self.rect().height()
        for vertex in self._vertices:
            vertex.setPos(QPointF(
                vertex.pos().x() * scale_x, vertex.pos().y() * scale_y
            ))

    def moveAnchorPointBy(self : Self, name : str, delta : QPointF) -> None:
        BaseRectangleMixin.moveAnchorPointBy(self, name, delta)
