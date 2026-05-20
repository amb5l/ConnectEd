from typing import Self
from enum   import StrEnum

from PyQt6.QtCore    import QPointF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem

from ....app import logger

from ....core.check import checked

from ..scenes import withScene

from .net_label import NetLabelItem

from .mixin              import ItemMixin
from .mixin.settings     import ItemSettingsMixin
from .mixin.presentation import ItemPresentationMixin
from .mixin.select       import ItemSelectMixin
from .mixin.change       import ItemChangeMixin

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
    ItemSettingsMixin,
    ItemPresentationMixin,
    ItemSelectMixin,
    ItemChangeMixin,
    QGraphicsPathItem
):
    _JUNCTION_THRESHOLD : int

    # instance attributes
    _state : NodeState

    @checked
    def __init__(self : Self, parent : QGraphicsItem | None = None) -> None:
        super().__init__(parent)
        self._state = NodeState.UNCONNECTED
        self.initItem()
        self.onSettingsChanged()

    def onScenePositionChanged(self : Self, _pos : QPointF) -> None:
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
        self.onSceneChanged()  # update pen, brush and graphics

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

    @checked
    def toXml(self : Self, xw : QXmlStreamWriter, id : int) -> None:
        xw.writeStartElement(self.settingsName())
        xw.writeAttribute("ID", str(id))
        xw.writeAttribute("X", str(self.scenePos().x()))
        xw.writeAttribute("Y", str(self.scenePos().y()))
        # serialise child items (NetLabelItem instances)
        for child in self.childItems():
            if isinstance(child, NetLabelItem):
                child.toXml(xw)
            else:
                logger().warning(f"Unexpected child item: {child.type()}")
        xw.writeEndElement()

    def _penKey(self : Self) -> tuple[NodeState, bool]:
        return (self._state, self.isSelected())

    def _brushKey(self : Self) -> tuple[NodeState, bool]:
        return (self._state, self.isSelected())

    def _updateGraphics(self : Self, scene : "DiagramScene") -> None:
        self.setPath(scene.resources.path(self.resourcesName(), self._state))


class FreeNodeItem(NodeItem):
    _JUNCTION_THRESHOLD = 3

    @checked
    def __init__(
        self : Self,
        pos  : QPointF | None = None
    ) -> None:
        super().__init__()
        if pos is not None:
            self.setPos(pos)

    @classmethod
    @checked
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        instance : "FreeNodeItem" = cls()
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
        # create child items (NetLabelItem instances)
        while not (xr.isEndElement() and xr.name() == "FreeNode"):
            if xr.isStartElement():
                item_name = xr.name()
                if item_name == "NetLabel":
                    child = NetLabelItem.fromXml(xr)
                    instance.setParentItem(child)
                else:
                    logger().warning(f"Unexpected child item: {item_name}")
            xr.readNext()
        return instance


class FixedNodeItem(NodeItem):
    _JUNCTION_THRESHOLD = 2

    @checked
    def onSelectionChanged(self : Self, selected : bool) -> None:
        super().onSelectionChanged(selected)
        parent = self.parentItem()
        if parent is not None:
            parent.setSelected(selected)

    @checked
    def toXml(self : Self, xw : QXmlStreamWriter, id : int) -> None:
        xw.writeStartElement(self.settingsName())
        xw.writeAttribute("ID", str(id))
        xw.writeAttribute("X", str(self.scenePos().x()))
        xw.writeAttribute("Y", str(self.scenePos().y()))
        xw.writeEndElement()

    @classmethod
    @checked
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


class TapMajorNodeItem(FixedNodeItem):
    pass


class TapMinorNodeItem(FixedNodeItem):
    pass


# Pin/tap attachment nodes used by diagram connectivity APIs (not free vertices).
PinNodeItem = FixedNodeItem
TapNodeItem = TapMajorNodeItem | TapMinorNodeItem
AttachedNodeItem = FixedNodeItem | TapMajorNodeItem | TapMinorNodeItem
