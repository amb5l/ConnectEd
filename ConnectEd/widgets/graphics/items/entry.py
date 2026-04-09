from typing import Self

from PyQt6.QtCore import QPointF, QXmlStreamWriter, QXmlStreamReader

from ....app import logger

from .node import NodeItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.diagram import DiagramScene
    from .port_pin import PortPinMixin
    from .port     import PortItem


class EntryItem(NodeItem):
    _JUNCTION_THRESHOLD = 2

    def __init__(
        self   : Self,
        parent : "PortPinMixin | None" = None
    ) -> None:
        super().__init__(parent=parent)

    def name(self : Self) -> str | None:
        parent : "PortPinMixin | None" = self.parentItem()
        return parent.name() if isinstance(parent, PortItem) else None

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
