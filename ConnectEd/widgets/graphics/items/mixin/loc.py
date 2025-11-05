from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from .....app import logger

from ...properties import PropertySpec, PropertiesMixin

from .. import EdgeLoc, Edge

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..block import Block


# TODO - merge into Block, which is the only item that uses it?
class ItemLocMixin:
    # instance attributes
    _loc : EdgeLoc

    _PROPERTY_SPECS_LOC = {
        "Edge" : PropertySpec(
            type_name   = "Edge",
            getter      = lambda self: self.loc().edge,
            setter      = lambda self, value: self.setLocEdge(value),
            description = "Parent edge"
        ),
        "Offset" : PropertySpec(
            type_name   = "float",
            getter      = lambda self: self.loc().offset,
            setter      = lambda self, value: self.setLocOffset(value),
            description = "Offset from start of parent edge"
        )
    }

    def initLoc(self : Self) -> None:
        self._loc = EdgeLoc(Edge.UNDEFINED, 0)

    def onParentChange(self : Self, parent : QGraphicsItem | None) -> None:
        """Update position when parent changes."""
        if hasattr(self, '_loc') \
        and parent is not None \
        and self._loc.edge != Edge.UNDEFINED:
            self.setLoc(self._loc)

    def loc(self : Self) -> EdgeLoc:
        return self._loc

    def setLoc(self : Self, loc : EdgeLoc) -> None:
        self._loc = loc
        self.prepareGeometryChange()
        match loc.edge:
            case Edge.LEFT   : angle = 0
            case Edge.RIGHT  : angle = 180
            case Edge.TOP    : angle = 90
            case Edge.BOTTOM : angle = 270
            case _ :
                logger().error(f"Invalid edge: {loc.edge}")
                angle = 0
        self.setRotation(angle)
        parent : "Block" = self.parentItem()
        edge_pos = parent.loc2pos(loc) if parent else QPointF()
        super().setPos(edge_pos)

    def setLocEdge(self : Self, edge : Edge) -> None:
        self.setLoc(EdgeLoc(Edge(edge), self._loc.offset))

    def setLocOffset(self : Self, offset : float) -> None:
        self.setLoc(EdgeLoc(self._loc.edge, offset))

    def locSnap(self : Self, loc : EdgeLoc, snap : QPointF | None = None) -> EdgeLoc:
        e = loc.edge
        if snap is None:
            d = loc.offset
        elif loc.edge in [Edge.LEFT, Edge.RIGHT]:
            d = round(loc.offset / snap.x()) * snap.x()
        else:
            d = round(loc.offset / snap.y()) * snap.y()
        return EdgeLoc(e, d)

    def pos(self : Self) -> QPointF:
        raise NotImplementedError("pos is not implemented for ItemLocMixin")

    def setPos(self : Self, _ : QPointF) -> None:
        raise NotImplementedError("setPos is not implemented for ItemLocMixin")
