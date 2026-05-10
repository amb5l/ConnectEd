from typing import Self
from enum   import StrEnum

from PyQt6.QtCore    import QPointF, QRectF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem

from ....app import settings, logger

from .property_label import PropertyLabelItem

from .mixin        import ItemMixin
from .mixin.shape  import ItemShapeMixin
from .mixin.paint  import ItemPaintMixin
from .mixin.change import ItemChangeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.diagram import DiagramScene
    from .segment  import SegmentItem
    from .port_pin import PortPinMixin
    from .tap      import TapItem


class NodeItem(
    ItemMixin,
    ItemShapeMixin,
    ItemPaintMixin,
    ItemChangeMixin,
    QGraphicsPathItem
):
    class State(StrEnum):
        UNCONNECTED = "unconnected"
        CONNECTED   = "connected"
        JUNCTION    = "junction"

    _JUNCTION_THRESHOLD : int

    # instance attributes
    _state : State

    def __init__(self : Self, parent : QGraphicsItem | None = None) -> None:
        super().__init__(parent)
        self._state = self.State.UNCONNECTED
        self.initItem()

    def onSceneChange(self : Self, scene : "DiagramScene | None") -> None:
        if scene is not None:
            self.onSettingsChange(scene)

    def onSettingsChange(self : Self, scene : "DiagramScene | None" = None) -> None:
        if scene is None:
            if (scene := self.scene()) is None:
                return
        item_name = self.settingsName()  # e.g. "PinNode" or "FreeNode"
        state_str = self._state.value    # e.g. "unconnected"
        self.setPen(scene.resources[item_name][state_str]["pen"])
        self.setBrush(scene.resources[item_name][state_str]["brush"])
        self._setPath(scene, item_name, state_str)

    def onScenePositionChange(self : Self, _pos : QPointF) -> None:
        """Update all connected segments."""
        for segment in self.segments():
            segment.onGeometryChange()

    def onConnectionChange(self : Self, scene : "DiagramScene | None" = None) -> None:
        if scene is None:
            if (scene := self.scene()) is None:
                return
        n = self.degree()
        self._state = \
            self.State.JUNCTION    if n >= self._JUNCTION_THRESHOLD else \
            self.State.CONNECTED   if n >= 1 else \
            self.State.UNCONNECTED
        self.onSettingsChange(scene)

    def name(self : Self) -> str | None:
        for child in self.childItems():
            if isinstance(child, PropertyLabelItem):
                return child.name()
        return None

    def degree(self : Self) -> int:
        scene : "DiagramScene | None" = self.scene()
        if scene is None or not scene.netlist.hasNode(self):
            return 0
        return scene.netlist.nodeDegree(self)

    def segments(self : Self) -> list["SegmentItem"]:
        scene : "DiagramScene | None" = self.scene()
        if scene is None or not scene.netlist.hasNode(self):
            return []
        return scene.netlist.segments(self)

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

    def _setPath(
        self      : Self,
        scene     : "DiagramScene | None" = None,
        item_name : str | None = None,
        state_str : str | None = None
    ) -> None:
        # ensure scene resources are available
        if scene is None:
            if (scene := self.scene()) is None:
                return
        item_name = self.settingsName() if item_name is None else item_name
        state_str = self._state.value if state_str is None else state_str
        path = scene.resources[item_name][state_str]["path"]
        self.setPath(path)
        size = settings().get(f"theme/items/{item_name}/size")
        self._hshape.clear()
        self._hshape.addRect(QRectF(-size/2, -size/2, size, size))


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


class NonFreeNodeItem(NodeItem):
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
            if isinstance(item, NonFreeNodeItem):
                instance = item
                break
        else:
            logger().warning("No PinNode found at {pos.x()}, {pos.y()}")
            instance = None
        xr.readNext()
        return instance


class PortPinNodeItem(NonFreeNodeItem):
    _JUNCTION_THRESHOLD = 2


class PortNodeItem(PortPinNodeItem):
    pass


class PinNodeItem(PortPinNodeItem):
    pass


class TapNodeItem(NonFreeNodeItem):
    _JUNCTION_THRESHOLD = 3
