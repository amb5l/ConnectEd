from __future__ import annotations

from typing import Self, Any

from PyQt6.QtCore    import QPointF, QLineF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsItem, QMenu
from PyQt6.QtGui     import QAction

from ....app import logger, settings

from ....core.check import checked
from ....core.defs  import Z_SEGMENT
from ....core.types import Axis, NetKind

from ..scenes import withScene

from .role import FunctionalItem

from .mixin              import ItemMixin
from .mixin.presentation import ItemPresentationMixin
from .mixin.select       import ItemSelectMixin
from .mixin.change       import ItemChangeMixin
from .mixin.clone        import ItemCloneMixin
from .mixin.xml          import ItemXmlMixin
from .mixin.menu         import ItemMenuMixin

from .node import NodeItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.diagram import DiagramScene
    from ..views.diagram  import DiagramView


class SegmentItem(
    FunctionalItem,
    ItemMixin,
    ItemPresentationMixin,
    ItemSelectMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    QGraphicsLineItem
):
    """Runs between two NodeItem instances."""
    # class attributes
    Z = Z_SEGMENT

    # instance attributes
    _node1    : NodeItem | None
    _node2    : NodeItem | None
    _line     : QLineF
    _ortho    : bool
    _net_kind : NetKind

    @checked
    def __init__(
        self  : Self,
        node1 : NodeItem | None = None,
        node2 : NodeItem | None = None
    ) -> None:
        QGraphicsLineItem.__init__(self)
        self._node1    = None
        self._node2    = None
        self._line     = QLineF()
        self._ortho    = True
        self._net_kind = NetKind.UNRESOLVED
        self.initItem()
        self.setNode1(node1)
        self.setNode2(node2)

    def onGeometryChanged(self : Self) -> None:
        v1 = self._node1
        v2 = self._node2
        if v1 is None or v2 is None:
            return
        p1 = v1.scenePos()
        p2 = v2.scenePos()
        self.setPos(p1)
        self._line.setP2(p2 - p1)
        self.setLine(self._line)
        self._ortho = self._line.dx() == 0 or self._line.dy() == 0

    def node1(self : Self) -> NodeItem | None:
        return self._node1

    @checked
    def setNode1(self : Self, node1 : NodeItem | None) -> None:
        self._setEndpoint(1, node1)

    def node2(self : Self) -> NodeItem | None:
        return self._node2

    @checked
    def setNode2(self : Self, node2 : NodeItem | None) -> None:
        self._setEndpoint(2, node2)

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

    def netKind(self : Self) -> NetKind:
        return self._net_kind

    @withScene
    def onConnectivityChanged(
        self  : Self,
        scene : DiagramScene | None = None,
    ) -> None:
        from ..scenes.diagram import DiagramScene
        if not isinstance(scene, DiagramScene):
            logger().error("Bad scene")
            return
        kind = scene.netlist.netKindForSegment(self)
        if kind == self._net_kind:
            return
        self._net_kind = kind
        self._updatePen(scene)

    @withScene
    def onSceneChanged(self : Self, scene : DiagramScene | None) -> None:
        from ..scenes.diagram import DiagramScene
        if isinstance(scene, DiagramScene):
            self._net_kind = scene.netlist.netKindForSegment(self)
        ItemPresentationMixin.onSceneChanged(self, scene)

    def isOrthogonal(self : Self) -> bool:
        return self._ortho

    def isDiagonal(self : Self) -> bool:
        return not self._ortho

    def axis(self : Self) -> Axis | None:
        if not self.isOrthogonal():
            return None
        return Axis.H if self.line().dy() == 0.0 else Axis.V

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
        view  : DiagramView,
        spos  : QPointF
    ) -> list[QAction | QMenu]:
        return [
            view.action(
                "Add Net Label",
                lambda: view.placeNetLabelOnSegment(self, spos)
            )
        ]

    @checked
    def toXml(
        self : Self,
        xw   : QXmlStreamWriter,
        ids  : tuple[int, int] | None = None
    ) -> None:
        if self._node1 is None or self._node2 is None:
            logger().error("Uninitialized nodes")
            return
        self.toXmlBegin(xw)
        if ids is None:
            # use node scene positions
            p1 = self._node1.scenePos()
            p2 = self._node2.scenePos()
            xw.writeAttribute("X1", f"{p1.x()}")
            xw.writeAttribute("Y1", f"{p1.y()}")
            xw.writeAttribute("X2", f"{p2.x()}")
            xw.writeAttribute("Y2", f"{p2.y()}")
        else:
            # use node IDs
            xw.writeAttribute("ID1", str(ids[0]))
            xw.writeAttribute("ID2", str(ids[1]))
        self.toXmlEnd(xw)

    @checked
    def _subscribeNode(self : Self, node : NodeItem) -> None:
        node.subscribe("scenePos", self, "onGeometryChanged")

    @checked
    def _unsubscribeNode(self : Self, node : NodeItem) -> None:
        node.unsubscribe("scenePos", self)

    @checked
    def _setEndpoint(self : Self, which : int, node : NodeItem | None) -> None:
        if (old := self._node1 if which == 1 else self._node2) is not None:
            self._unsubscribeNode(old)
        if which == 1:
            self._node1 = node
        else:
            self._node2 = node
        if node is not None:
            self._subscribeNode(node)
        self.onGeometryChanged()

    def _resourceKey(self : Self) -> tuple[NetKind, bool]:
        return (self._net_kind, self.isSelected())

    def _resourceKeyDefault(self : Self) -> tuple[NetKind, bool]:
        return (NetKind.UNRESOLVED, False)


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

    @checked
    @classmethod
    def fromXml(cls : type[Self], xr : QXmlStreamReader) -> Self:
        """Load clipboard/document segment geometry into a preview line."""
        attrs = xr.attributes()
        instance = cls()
        x1 = attrs.value("X1")
        if x1:
            p1 = QPointF(float(x1), float(attrs.value("Y1")))
            p2 = QPointF(float(attrs.value("X2")), float(attrs.value("Y2")))
            instance.setP1P2(p1, p2)
        else:
            logger().warning("Segment missing X1/Y1/X2/Y2 attributes")
        xr.readNext()
        return instance

    @withScene
    def _updatePen(self : Self, scene : DiagramScene) -> None:
        self.setPen(scene.resources.pen(self._RESOURCE_NAME))


class SegmentPreview1Item(SegmentPreviewItem):
    _RESOURCE_NAME = "SegmentPreview1"


class SegmentPreview2Item(SegmentPreviewItem):
    _RESOURCE_NAME = "SegmentPreview2"
