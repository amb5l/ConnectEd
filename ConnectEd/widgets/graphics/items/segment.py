from typing import Self, Any

from PyQt6.QtCore    import QPointF, QLineF
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsItem, QMenu
from PyQt6.QtGui     import QAction

from ....app import settings

from ....core.check import checked
from ....core.defs import Z_SEGMENT

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
    from ..views.diagram  import DiagramView


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
    Z = Z_SEGMENT

    # instance attributes
    _node1 : NodeItem | None
    _node2 : NodeItem | None
    _line  : QLineF
    _ortho : bool

    @checked
    def __init__(
        self  : Self,
        node1 : NodeItem | None = None,
        node2 : NodeItem | None = None
    ) -> None:
        QGraphicsLineItem.__init__(self)
        self._line  = QLineF()
        self._ortho = True
        self.initItem()
        self.setNode1(node1)
        self.setNode2(node2)

    def onGeometryChanged(self : Self) -> None:
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
        ortho = self._line.dx() == 0 or self._line.dy() == 0
        if ortho != self._ortho:
            self._ortho = ortho
            scene = self.scene()
            if scene is not None:
                self._updatePen(scene)
        else:
            self._ortho = ortho

    def node1(self : Self) -> NodeItem | None:
        return self._node1

    @checked
    def setNode1(self : Self, node1 : NodeItem | None) -> None:
        self._node1 = node1
        self.onGeometryChanged()

    def node2(self : Self) -> NodeItem | None:
        return self._node2

    @checked
    def setNode2(self : Self, node2 : NodeItem | None) -> None:
        self._node2 = node2
        self.onGeometryChanged()

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

    def isOrthogonal(self : Self) -> bool:
        return self._ortho

    def isDiagonal(self : Self) -> bool:
        return not self._ortho

    def sceneMidpoint(self : Self) -> QPointF:
        return self.scenePos() + self.line().p2() / 2

    def sceneLine(self : Self) -> QLineF:
        return QLineF(self.scenePos(), self.mapToScene(self.line().p2()))

    def perpendicularIntersection(self : Self, spos : QPointF) -> QPointF:
        """Perpendicular foot of *spos* on this segment (clamp to endpoints)."""
        p1   = self.sceneLine().p1()
        p2   = self.sceneLine().p2()
        dx   = p2.x() - p1.x()
        dy   = p2.y() - p1.y()
        len2 = dx * dx + dy * dy
        if len2 == 0.0:
            return p1
        t = ((spos.x() - p1.x()) * dx + (spos.y() - p1.y()) * dy) / len2
        if t <= 0.0:
            return p1
        if t >= 1.0:
            return p2
        return QPointF(p1.x() + t * dx, p1.y() + t * dy)

    @checked
    def ctxMenuItems(
        self  : Self,
        view  : "DiagramView",
        spos  : QPointF
    ) -> list[QAction | QMenu]:
        return [
            view.action(
                "Add Net Label",
                lambda: view.ui.placeNetLabelOnSegment(self, spos)
            )
        ]

    def _penKey(self : Self) -> tuple[bool, bool]:
        return (self.isDiagonal(), self.isSelected())

    def _penKeyDefault(self : Self) -> tuple[bool, bool]:
        return (False, False)


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
