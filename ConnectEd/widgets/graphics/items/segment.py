from typing import Self

from PyQt6.QtCore    import Qt, QPointF, QLineF
from PyQt6.QtWidgets import QGraphicsLineItem

from ....core.defs import Z_DRAWING

from .mixin        import ItemMixin, ItemSettingsMixin
from .mixin.line   import ItemLineMixin
from .mixin.change import ItemChangeMixin
from .mixin.clone  import ItemCloneMixin
from .mixin.menu   import ItemMenuMixin

from .node import NodeItem


class SegmentItem(
    ItemMixin,
    ItemLineMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemMenuMixin,
    QGraphicsLineItem
):
    """Runs between two NodeItem instances."""
    # class attributes
    Z = Z_DRAWING - 1
    _PEN_CAP_STYLE = Qt.PenCapStyle.RoundCap

    # instance attributes
    _node1 : NodeItem | None
    _node2 : NodeItem | None
    _line  : QLineF

    def __init__(
        self  : Self,
        node1 : NodeItem | None = None,
        node2 : NodeItem | None = None
    ) -> None:
        QGraphicsLineItem.__init__(self)
        self._line = QLineF()
        self.initItem()
        self.setNode1(node1)
        self.setNode2(node2)

    def onGeometryChange(self : Self) -> None:
        if not hasattr(self, "_node1") or not hasattr(self, "_node2"):
            return
        v1 = self._node1
        v2 = self._node2
        if v1 is None or v2 is None:
            return
        p1 = v1.scenePos() if isinstance(v1, NodeItem) else v1
        p2 = v2.scenePos() if isinstance(v2, NodeItem) else v2
        self.setPos(p1)
        self._line.setP2(p2-p1)
        self.setLine(self._line)

    def node1(self : Self) -> NodeItem | None:
        return self._node1

    def setNode1(self : Self, node1 : NodeItem | None) -> None:
        self._node1 = node1
        self.onGeometryChange()

    def node2(self : Self) -> NodeItem | None:
        return self._node2

    def setNode2(self : Self, node2 : NodeItem | None) -> None:
        self._node2 = node2
        self.onGeometryChange()

    def changeNode(self : Self, old : NodeItem, new : NodeItem) -> bool:
        if self._node1 is old:
            self.setNode1(new)
            return True
        elif self._node2 is old:
            self.setNode2(new)
            return True
        return False

    def otherNode(self : Self, node : NodeItem) -> NodeItem | None:
        if self._node1 is node:
            return self._node2
        elif self._node2 is node:
            return self._node1
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
