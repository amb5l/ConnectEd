from typing import Self
from enum   import StrEnum

from PyQt6.QtCore    import QPointF, QRectF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsPathItem

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


class VertexItem(
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

    _JUNCTION_THRESHOLD = 3

    # instance attributes
    _state : State

    def __init__(
        self   : Self,
        pos    : QPointF | None = None,
        parent : "PortPinMixin | None" = None
    ) -> None:
        super().__init__(parent)
        if pos is not None:
            self.setPos(pos)
        self._state = self.State.UNCONNECTED
        self.initItem()

    def onSceneChange(self : Self, scene : "DiagramScene | None") -> None:
        if scene is not None:
            self.onSettingsChange(scene)

    def onSettingsChange(self : Self, scene : "DiagramScene | None" = None) -> None:
        if scene is None:
            if (scene := self.scene()) is None:
                return
        item_name = self.settingsName()  # "Entry" or "Vertex"
        state_str = self._state.value  # e.g. "unconnected"
        self.setPen(scene.resources[item_name][state_str]["pen"])
        self.setBrush(scene.resources[item_name][state_str]["brush"])
        self._updatePath(scene, item_name, state_str)

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

    def degree(self : Self) -> int:
        scene : "DiagramScene | None" = self.scene()
        if scene is None or self not in scene._graph:
            return 0
        return scene._graph.degree(self)

    def segments(self : Self) -> list["SegmentItem"]:
        scene : "DiagramScene | None" = self.scene()
        if scene is None or self not in scene._graph:
            return []
        return [
            data["segment"] for _, _, data in scene._graph.edges(self, data=True)
        ]

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

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        instance : "VertexItem" = cls(fresh=False)
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
        while not (xr.isEndElement() and xr.name() == "Vertex"):
            if xr.isStartElement():
                item_name = xr.name()
                if item_name == "NetPropertyText":
                    child = PropertyLabelItem.fromXml(xr)
                    instance.setParentItem(child)
                else:
                    logger().warning(f"Unexpected child item: {item_name}")
            xr.readNext()
        return instance

    def _updatePath(
        self      : Self,
        scene     : "DiagramScene | None" = None,
        item_name : str | None = None,
        state_str : str | None = None
    ) -> None:
        if scene is None:
            if (scene := self.scene()) is None:
                return
        if item_name is None:
            item_name = self.settingsName()
        if state_str is None:
            state_str = self._state.value
        path = scene.resources[item_name][state_str]["path"]
        self.setPath(path)
        size = settings().get(f"theme/items/{item_name}/size")
        self._hshape.clear()
        self._hshape.addRect(QRectF(-size/2, -size/2, size, size))


class EntryItem(VertexItem):
    _JUNCTION_THRESHOLD = 2

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
        Entries are created when pins/ports are deserialised,
        so here we are checking that the entry exists.
        """

        pos = QPointF(
            float(xr.attributes().value("X")),
            float(xr.attributes().value("Y"))
        )
        items = scene.items(pos)
        for item in items:
            if isinstance(item, EntryItem):
                instance = item
                break
        else:
            logger().warning("No entry found at {pos.x()}, {pos.y()}")
            instance = None
        xr.readNext()
        return instance
