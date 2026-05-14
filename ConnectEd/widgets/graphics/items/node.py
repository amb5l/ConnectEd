from typing import Self
from enum   import StrEnum

from PyQt6.QtCore    import QPointF, QRectF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem

from ....app import settings, logger

from ..scenes import withScene

from .property_label import PropertyLabelItem

from .mixin        import ItemMixin
from .mixin.shape  import ItemShapeMixin
from .mixin.paint  import ItemPaintMixin
from .mixin.change import ItemChangeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.diagram import DiagramScene
    from .segment  import SegmentItem


class NodeState(StrEnum):
    UNCONNECTED = "unconnected"
    CONNECTED   = "connected"
    JUNCTION    = "junction"


class NodeItem(
    ItemMixin,
    ItemShapeMixin,
    ItemPaintMixin,
    ItemChangeMixin,
    QGraphicsPathItem
):
    _JUNCTION_THRESHOLD : int

    # instance attributes
    _state : NodeState

    def __init__(self : Self, parent : QGraphicsItem | None = None) -> None:
        super().__init__(parent)
        self._state = NodeState.UNCONNECTED
        self.initItem()

    def onSettingsChange(self : Self) -> None:
        self.onSceneChange()

    @withScene
    def onSceneChange(self : Self, scene : "DiagramScene | None") -> None:
        self._updatePenBrush(scene)
        self.setPath(scene.rsrcman.path(self.__class__, self._state))
        self._hshape.clear()
        self._hshape.addRect(self.boundingRect())

    def onSelectionChange(self : Self, selected : bool) -> None:
        self._updatePenBrush(self.scene())

    def onScenePositionChange(self : Self, _pos : QPointF) -> None:
        """Update all connected segments."""
        for segment in self.segments():
            segment.onGeometryChange()

    @withScene
    def onConnectionChange(self : Self, scene : "DiagramScene | None" = None) -> None:
        n = self.degree()
        self._state = \
            NodeState.JUNCTION    if n >= self._JUNCTION_THRESHOLD else \
            NodeState.CONNECTED   if n >= 1 else \
            NodeState.UNCONNECTED
        self.onSettingsChange(scene)

    def degree(self : Self) -> int:
        scene : "DiagramScene | None" = self.scene()
        if scene is None or not scene.netlist.hasNode(self):
            return 0
        return scene.netlist.nodeDegree(self)

    def segments(self : Self) -> list["SegmentItem"]:
        scene : "DiagramScene | None" = self.scene()
        if scene is None or not scene.netlist.hasNode(self):
            return []
        return scene.netlist.nodeSegments(self)

    def toXml(self : Self, xw : QXmlStreamWriter, id : int) -> None:
        xw.writeStartElement(self.settingsName())
        xw.writeAttribute("ID", str(id))
        xw.writeAttribute("X", str(self.scenePos().x()))
        xw.writeAttribute("Y", str(self.scenePos().y()))
        # serialise child items (PropertyLabelItem instances)
        for child in self.childItems():
            if isinstance(child, PropertyLabelItem):
                child.toXml(xw)
            else:
                logger().warning(f"Unexpected child item: {child.type()}")
        xw.writeEndElement()

    def _updatePenBrush(self : Self, scene : "DiagramScene") -> None:
        key = (self._state, self.isSelected())
        self.setPen(scene.rsrcman.pen(self.__class__, key))
        self.setBrush(scene.rsrcman.brush(self.__class__, key))


class FreeNodeItem(NodeItem):
    _JUNCTION_THRESHOLD = 3

    def __init__(
        self : Self,
        pos  : QPointF | None = None
    ) -> None:
        super().__init__()
        if pos is not None:
            self.setPos(pos)

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        instance : "FreeNodeItem" = cls(fresh=False)
        for attr_name, attr_value in xr.attributes():
            match attr_name:
                case "ID":
                    pass
                case "X":
                    instance.setX(float(attr_value))
                case "Y":
                    instance.setY(float(attr_value))
                case _:
                    logger().warning(f"Unexpected attribute: {attr_name}={attr_value}")
        # create child items (PropertyLabelItem instances)
        while not (xr.isEndElement() and xr.name() == "FreeNode"):
            if xr.isStartElement():
                item_name = xr.name()
                if item_name == "NetPropertyText":
                    child = PropertyLabelItem.fromXml(xr)
                    instance.setParentItem(child)
                else:
                    logger().warning(f"Unexpected child item: {item_name}")
            xr.readNext()
        return instance


class FixedNodeItem(NodeItem):
    _JUNCTION_THRESHOLD = 2

    def onSelectionChange(self : Self, selected : bool) -> None:
        super().onSelectionChange(selected)
        parent = self.parentItem()
        if parent is not None:
            parent.setSelected(selected)

    def toXml(self : Self, xw : QXmlStreamWriter, id : int) -> None:
        xw.writeStartElement(self.settingsName())
        xw.writeAttribute("ID", str(id))
        xw.writeAttribute("X", str(self.scenePos().x()))
        xw.writeAttribute("Y", str(self.scenePos().y()))
        xw.writeEndElement()

    @classmethod
    def fromXml(
        cls   : Self,
        xr    : QXmlStreamReader,
        scene : "DiagramScene"
    ) -> Self | None:
        """
        Non free nodes are created when pins/ports/taps are deserialised,
        so here we are just checking that the node exists.
        """
        pos = QPointF(
            float(xr.attributes().value("X")),
            float(xr.attributes().value("Y"))
        )
        items = scene.items(pos)
        for item in items:
            if isinstance(item, FixedNodeItem):
                instance = item
                break
        else:
            logger().warning("No FixedNode found at {pos.x()}, {pos.y()}")
            instance = None
        xr.readNext()
        return instance


class TapNodeItem(FixedNodeItem):
    def settingsName(self : Self) -> str:
        return "FixedNode"


class TapMajorNodeItem(TapNodeItem):
    pass


class TapMinorNodeItem(TapNodeItem):
    pass
