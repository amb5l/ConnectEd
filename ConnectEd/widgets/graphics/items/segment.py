from typing import Self, Any

from PyQt6.QtCore    import QPointF, QLineF
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsItem

from ....app import settings

from ....core.check import checked
from ....core.defs import Z_DRAWING

from ..scenes import withScene

from .mixin              import ItemMixin
from .mixin.presentation import ItemPresentationMixin
from .mixin.select       import ItemSelectMixin
from .mixin.change       import ItemChangeMixin
from .mixin.clone        import ItemCloneMixin
from .mixin.menu         import ItemMenuMixin

from .node import NodeItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene


class SegmentItem(
    ItemMixin,
    ItemPresentationMixin,
    ItemSelectMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemMenuMixin,
    QGraphicsLineItem
):
    """Runs between two NodeItem instances."""
    # class attributes
    Z = Z_DRAWING - 1

    # instance attributes
    _node1 : NodeItem | None
    _node2 : NodeItem | None
    _line  : QLineF

    @checked
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

    @checked
    def setNode1(self : Self, node1 : NodeItem | None) -> None:
        self._node1 = node1
        self.onGeometryChange()

    def node2(self : Self) -> NodeItem | None:
        return self._node2

    @checked
    def setNode2(self : Self, node2 : NodeItem | None) -> None:
        self._node2 = node2
        self.onGeometryChange()

    @checked
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


# TODO link to settings/resources
class SegmentPreviewItem(QGraphicsLineItem):
    # class attributes
    _RESOURCE_NAME : str

    @checked
    def __init__(self : Self) -> None:
        QGraphicsLineItem.__init__(self)
        self.onSettingsChanged()
        settings().changed.connect(self.onSettingsChanged)

    def itemChange(
        self : Self,
        change : QGraphicsItem.GraphicsItemChange,
        value : Any
    ) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemSceneHasChanged:
            if value is not None:
                self._updatePen(value)
        return super().itemChange(change, value)

    def onSettingsChanged(self : Self) -> None:
        self._updatePen(self.scene())

    def p1(self : Self) -> QPointF:
        return self.pos()

    @checked
    def setP1(self : Self, pos : QPointF) -> None:
        self.setP1P2(pos, self.p2())

    def p2(self : Self) -> QPointF:
        return self.pos() + self.line().p2()

    @checked
    def setP2(self : Self, pos : QPointF) -> None:
        self.setP1P2(self.pos(), pos)

    @checked
    def setP1P2(self : Self, p1 : QPointF, p2 : QPointF) -> None:
        self.setPos(p1)
        line = self.line()
        line.setP2(p2-p1)
        self.setLine(line)

    @withScene
    def _updatePen(self : Self, scene : "DrawingScene") -> None:
        self.setPen(scene.resources.pen(self._RESOURCE_NAME))


class SegmentPreview1Item(SegmentPreviewItem):
    _RESOURCE_NAME = "SegmentPreview1"


class SegmentPreview2Item(SegmentPreviewItem):
    _RESOURCE_NAME = "SegmentPreview2"
