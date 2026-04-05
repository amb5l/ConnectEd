from typing import Self

from PyQt6.QtCore    import Qt, QPointF, QLineF
from PyQt6.QtWidgets import QGraphicsLineItem

from ....core.defs import Z_DRAWING

from .mixin        import ItemMixin, ItemSettingsMixin
from .mixin.line   import ItemLineMixin
from .mixin.change import ItemChangeMixin
from .mixin.clone  import ItemCloneMixin
from .mixin.menu   import ItemMenuMixin

from .vertex import VertexItem


class SegmentItem(
    ItemMixin,
    ItemLineMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemMenuMixin,
    QGraphicsLineItem
):
    """Runs between two VertexItem instances."""
    # class attributes
    Z = Z_DRAWING - 1
    _PEN_CAP_STYLE = Qt.PenCapStyle.SquareCap

    # instance attributes
    _vtx1 : VertexItem | None
    _vtx2 : VertexItem | None
    _line : QLineF

    def __init__(
        self : Self,
        vtx1 : VertexItem | None = None,
        vtx2 : VertexItem | None = None
    ) -> None:
        QGraphicsLineItem.__init__(self)
        self._line = QLineF()
        self.initItem()
        self.setVtx1(vtx1)
        self.setVtx2(vtx2)

    def onGeometryChange(self : Self) -> None:
        if not hasattr(self, "_vtx1") or not hasattr(self, "_vtx2"):
            return
        v1 = self._vtx1
        v2 = self._vtx2
        if v1 is None or v2 is None:
            return
        p1 = v1.scenePos() if isinstance(v1, VertexItem) else v1
        p2 = v2.scenePos() if isinstance(v2, VertexItem) else v2
        self.setPos(p1)
        self._line.setP2(p2-p1)
        self.setLine(self._line)

    def vtx1(self : Self) -> VertexItem | None:
        return self._vtx1

    def setVtx1(self : Self, vtx : VertexItem | None) -> None:
        self._vtx1 = vtx
        self.onGeometryChange()

    def vtx2(self : Self) -> VertexItem | None:
        return self._vtx2

    def setVtx2(self : Self, vtx : VertexItem | None) -> None:
        self._vtx2 = vtx
        self.onGeometryChange()

    def changeVtx(self : Self, old : VertexItem, new : VertexItem) -> bool:
        if self._vtx1 is old:
            self.setVtx1(new)
            return True
        elif self._vtx2 is old:
            self.setVtx2(new)
            return True
        return False

    def otherVtx(self : Self, vtx : VertexItem) -> VertexItem | None:
        if self._vtx1 is vtx:
            return self._vtx2
        elif self._vtx2 is vtx:
            return self._vtx1
        return None


class SegmentPreviewItem(
    ItemSettingsMixin,
    ItemChangeMixin,
    ItemLineMixin,
    QGraphicsLineItem
):
    def __init__(self : Self) -> None:
        QGraphicsLineItem.__init__(self)
        self.initChange()
        self.initLine()

    def p1(self : Self) -> QPointF:
        return self.pos()

    def setP1(self : Self, pos : QPointF) -> None:
        self.setP1P2(pos, self.p2())

    def p2(self : Self) -> QPointF:
        return self.pos() + self.line().p2()

    def setP2(self : Self, pos : QPointF) -> None:
        self.setP1P2(self.pos(), pos)

    def setP1P2(self : Self, p1 : QPointF, p2 : QPointF) -> None:
        self.setPos(p1)
        line = self.line()
        line.setP2(p2-p1)
        self.setLine(line)


class SegmentPreview1Item(SegmentPreviewItem):
    pass


class SegmentPreview2Item(SegmentPreviewItem):
    pass
