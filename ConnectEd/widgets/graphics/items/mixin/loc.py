from typing import Self

from PyQt6.QtCore import QPointF

from ...properties import PropertySpec

from .. import EdgeLoc, Edge

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..pin_rect import PinRect


class ElementLocMixin:
    # instance attributes
    _loc : EdgeLoc

    _PROPERTY_SPECS_LOC = {
        "Location (Edge)" : PropertySpec(
            type_name   = "str",
            getter      = lambda self: self.loc().edge,
            setter      = lambda self, value: self.setLocEdge(value),
            description = "Parent edge"
        ),
        "Location (Distance)" : PropertySpec(
            type_name   = "float",
            getter      = lambda self: self.loc().distance,
            setter      = lambda self, value: self.setLocDistance(value),
            description = "Distance from start of parent edge"
        )
    }

    def loc(self : Self) -> EdgeLoc:
        return self._loc

    def setLoc(self : Self, loc : EdgeLoc) -> None:
        self._loc = loc
        self.prepareGeometryChange()
        match loc.edge:
            case Edge.LEFT:   angle = 0
            case Edge.RIGHT:  angle = 180
            case Edge.TOP:    angle = 90
            case Edge.BOTTOM: angle = 270
        self.setRotation(angle)
        parent : "PinRect" = self.parentItem()
        edge_pos = parent.loc2pos(loc) if parent else QPointF()
        super().setPos(edge_pos)
        for child in self.childItems():
            for grandchild in child.childItems():
                if hasattr(grandchild, 'compensateRotation'):
                    grandchild.compensateRotation(angle)

    def setLocEdge(self : Self, edge : Edge) -> None:
        self.setLoc(EdgeLoc(Edge(edge), self._loc.distance))

    def setLocDistance(self : Self, distance : float) -> None:
        self.setLoc(EdgeLoc(self._loc.edge, distance))

    def locSnap(self : Self, loc : EdgeLoc, snap : QPointF | None = None) -> EdgeLoc:
        e = loc.edge
        if snap is None:
            d = loc.distance
        elif loc.edge in [Edge.LEFT, Edge.RIGHT]:
            d = round(loc.distance / snap.x()) * snap.x()
        else:
            d = round(loc.distance / snap.y()) * snap.y()
        return EdgeLoc(e, d)

    def pos(self : Self) -> QPointF:
        raise NotImplementedError("pos is not implemented for ElementLocMixin")

    def setPos(self : Self, _ : QPointF) -> None:
        raise NotImplementedError("setPos is not implemented for ElementLocMixin")
