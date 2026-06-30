from typing import Self, cast, overload

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem

from .....app import logger

from .....core.check import checked
from .....core.types import DataKind, EdgeLoc, Edge
from .....core.utils import qtItemClass

from ...properties import InherentProperty, PropertiesManager

from ..protocols import (
    OnSceneChangedProtocol,
    OnSceneOrientationChangedProtocol
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...scenes.diagram import DiagramScene


class ItemEdgeLocMixin:
    """
    Block and symbol pins use this mixin for edge location positioning.
    """

    # class attributes
    _PROPERTIES = {
        "Edge" : InherentProperty["ItemEdgeLocMixin"](
            kind   = DataKind.EDGE,
            getter = lambda self: self.loc().edge,
            setter = lambda self, value: self.setLocEdge(value)
        ),
        "Offset" : InherentProperty["ItemEdgeLocMixin"](
            kind   = DataKind.FLOAT,
            getter = lambda self: self.loc().offset,
            setter = lambda self, value: self.setLocOffset(value)
        )
    }

    # instance attributes
    _edge_loc : EdgeLoc

    # external instance attributes
    properties : PropertiesManager  # provided by PropertiesMixin

    @checked
    def initEdgeLoc(self : Self) -> None:
        self._edge_loc = EdgeLoc()

    @checked
    def onParentChanged(self : Self, parent : QGraphicsItem | None) -> None:
        """Update position when parent changes."""
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        if  parent is not None \
        and self._edge_loc.edge is not None \
        and self._edge_loc.offset is not None:
            self.setLoc(self._edge_loc)
            self.onRotationChanged(self.rotation())
            self.onMirrorChanged()
            from ...scenes.diagram import DiagramScene
            if  isinstance(scene := self.scene(), DiagramScene) \
            and isinstance(self, OnSceneChangedProtocol):
                self.onSceneChanged(scene)

    def onRotationChanged(self : Self, _angle : float) -> None:
        """Propagate rotation change to children."""
        host = cast(QGraphicsItem, self)
        for child in host.childItems():
            if isinstance(child, OnSceneOrientationChangedProtocol):
                child.onSceneOrientationChanged()

    def onMirrorChanged(self : Self) -> None:
        """Propagate mirror change to children."""
        host = cast(QGraphicsItem, self)
        for child in host.childItems():
            if isinstance(child, OnSceneOrientationChangedProtocol):
                child.onSceneOrientationChanged()

    def loc(self : Self) -> EdgeLoc:
        return self._edge_loc

    @checked
    def setLoc(self : Self, loc : EdgeLoc) -> None:
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        self._edge_loc = loc
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
        # Parent may be absent during XML load; onParentChanged reapplies.
        parent = self.parentItem()
        if not isinstance(parent, ItemLocParentMixin):
            return
        if loc.edge is None or loc.offset is None:
            return
        # Bypass the pos/setPos guards below — edge-loc items must not be
        # positioned via those APIs; setLoc is the only writer.
        qtItemClass(self).setPos(self, parent.loc2pos(loc))

    @checked
    def setLocEdge(self : Self, edge : Edge) -> None:
        self.setLoc(EdgeLoc(Edge(edge), self._edge_loc.offset))
        self.properties.signalChanges("Edge")

    @checked
    def setLocOffset(self : Self, offset : float) -> None:
        self.setLoc(EdgeLoc(self._edge_loc.edge, offset))
        self.properties.signalChanges("Offset")

    @checked
    def locSnap(
        self : Self,
        loc  : EdgeLoc,
        snap : QPointF | None = None
    ) -> EdgeLoc:
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        e = loc.edge
        d = loc.offset
        if e is None or d is None:
            return loc
        if snap is None:
            pass
        elif e in [Edge.LEFT, Edge.RIGHT]:
            d = round(d / snap.x()) * snap.x()
        else:
            d = round(d / snap.y()) * snap.y()
        return EdgeLoc(e, d)

    def pos(self : Self) -> QPointF:
        raise TypeError("Use loc() — edge-located items are not free-positioned")

    @overload
    def setPos(self, pos : QPointF) -> None: ...

    @overload
    def setPos(self, ax : float, ay : float) -> None: ...

    def setPos(self, *args, **kwargs) -> None:
        raise TypeError("Use setLoc() — edge-located items are not free-positioned")


class ItemLocParentMixin:
    @checked
    def pos2loc(self : Self, pos : QPointF) -> EdgeLoc:
        if not isinstance(self, QGraphicsRectItem):
            raise TypeError("Bad host")
        rect = self.rect()
        w = rect.width()
        h = rect.height()
        c = c = self.mapToParent(rect.center())  # scene pos of rectangle center
        r = pos - c  # pos relative to rectangle center
        hq = False if r.x() == 0 or abs(r.y()/r.x()) > abs(h/w) else True
        if hq:
            offset = min(max(r.y(), -h/2), h/2) + h/2
            edge = Edge.LEFT if r.x() <= 0 else Edge.RIGHT
        else:
            offset = min(max(r.x(), -w/2), w/2) + w/2
            edge = Edge.TOP if r.y() <= 0 else Edge.BOTTOM
        return EdgeLoc(edge, offset)

    @checked
    def loc2pos(self : Self, loc : EdgeLoc) -> QPointF:
        if not isinstance(self, QGraphicsRectItem):
            raise TypeError("Bad host")
        if loc.edge is None or loc.offset is None:
            return QPointF()
        match loc.edge:
            case Edge.LEFT:
                return QPointF(0, loc.offset)
            case Edge.RIGHT:
                return QPointF(self.rect().width(), loc.offset)
            case Edge.TOP:
                return QPointF(loc.offset, 0)
            case Edge.BOTTOM:
                return QPointF(loc.offset, self.rect().height())
            case _:
                raise ValueError(f"Invalid edge: {loc.edge}")

    @checked
    def loc2peri(self : Self, loc : EdgeLoc) -> float:
        if not isinstance(self, QGraphicsRectItem):
            raise TypeError("Bad host")
        if loc.edge is None or loc.offset is None:
            return 0
        rect = self.rect()
        w = rect.width()
        h = rect.height()
        d = loc.offset
        if loc.edge == Edge.LEFT:
            return d
        elif loc.edge == Edge.BOTTOM:
            return h + d
        elif loc.edge == Edge.RIGHT:
            return h + w + (h - d)
        elif loc.edge == Edge.TOP:
            return h + w + h + (w - d)
        else:
            raise ValueError(f"Invalid edge: {loc.edge}")

    @checked
    def peri2loc(self : Self, peri : float) -> EdgeLoc:
        if not isinstance(self, QGraphicsRectItem):
            raise TypeError("Bad host")
        rect = self.rect()
        w = rect.width()
        h = rect.height()
        p = 2 * (w + h)
        peri = peri % p if p > 0 else 0
        if peri < h:
            return EdgeLoc(Edge.LEFT, peri)
        elif peri < h + w:
            return EdgeLoc(Edge.BOTTOM, peri - h)
        elif peri < h + w + h:
            return EdgeLoc(Edge.RIGHT, h - (peri - h - w))
        else:
            return EdgeLoc(Edge.TOP, w - (peri - h - w - h))

    @checked
    def locDelta(self : Self, loc1 : EdgeLoc, loc2 : EdgeLoc) -> float:
        if not isinstance(self, QGraphicsRectItem):
            raise TypeError("Bad host")
        if None in (loc1.edge, loc1.offset, loc2.edge, loc2.offset):
            return 0
        rect = self.rect()
        w = rect.width()
        h = rect.height()
        p = 2 * (w + h)
        d = self.loc2peri(loc2) - self.loc2peri(loc1)
        if d >= 0: # CCW
            ccw_d = d % p
            cw_d = p - ccw_d
        else: # CW
            cw_d = -d % p
            ccw_d = p - cw_d
        return -cw_d if cw_d < ccw_d else ccw_d

    @checked
    def locOffset(
        self   : Self,
        loc    : EdgeLoc,
        offset : float,
        corner : int
    ) -> EdgeLoc:
        left, right, top, bottom = Edge.LEFT, Edge.RIGHT, Edge.TOP, Edge.BOTTOM
        if not isinstance(self, QGraphicsRectItem):
            raise TypeError("Bad host")
        rect = self.rect()
        w = rect.width()
        h = rect.height()
        def edgeLen(edge : Edge) -> float:
            return h if edge in [Edge.LEFT, Edge.RIGHT] else w
        def edgeNextCCW(edge : Edge) -> Edge | None:
            return \
                bottom if edge == left   else \
                right  if edge == bottom else \
                top    if edge == right  else \
                left   if edge == top    else \
                None
        def edgeNextCW(edge : Edge) -> Edge | None:
            return \
                top    if edge == left   else \
                right  if edge == top    else \
                bottom if edge == right  else \
                left   if edge == bottom else \
                None
        loc = self.peri2loc(self.loc2peri(loc) + offset)
        if offset >= 0 and corner == +1: # CCW
            if (loc.edge in [left, bottom] and loc.offset == edgeLen(loc.edge)) \
            or (loc.edge in [right, top] and loc.offset == 0):
                loc.edge = edgeNextCCW(loc.edge)
                loc.offset = edgeLen(loc.edge) \
                    if loc.edge in [right, top] else 0
        elif offset < 0 and corner == -1: # CW
            if (loc.edge in [top, right] and loc.offset == edgeLen(loc.edge)) \
            or (loc.edge in [bottom, left] and loc.offset == 0):
                loc.edge = edgeNextCW(loc.edge)
                loc.offset = edgeLen(loc.edge) \
                    if loc.edge in [bottom, left] else 0
        return loc
