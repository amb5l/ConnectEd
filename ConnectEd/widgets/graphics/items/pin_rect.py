from typing import Self, Optional

from PyQt6.QtCore    import QPointF, QSizeF

from . import EdgeLoc, Edge

from .base_rect import BaseRectangle

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView


class PinRect(BaseRectangle):
    def onGeometryChange(self : Self) -> None:
        super().onGeometryChange()
        # reposition pins
        #for item in self.childItems():
        #    if isinstance(item, Pin):
        #        item.onPositionChange()

    def getMenuItems(self : Self) -> list[str]:
        return ["Add Pin...", "-", "Appearance...", "Properties..."]

    def pos2loc(self : Self, pos : QPointF) -> EdgeLoc:
        w = self._rect.width()
        h = self._rect.height()
        c = self.pos() + self._rect.center() # scene pos of rectangle center
        r = pos - c                          # pos relative to rectangle center
        hq = False if r.x() == 0 or abs(r.y()/r.x()) > abs(h/w) else True
        if hq:
            distance = min(max(r.y(), -h/2), h/2) + h/2
            edge = Edge.LEFT if r.x() <= 0 else Edge.RIGHT
        else:
            distance = min(max(r.x(), -w/2), w/2) + w/2
            edge = Edge.TOP if r.y() <= 0 else Edge.BOTTOM
        return EdgeLoc(edge, distance)

    def loc2pos(self : Self, loc : EdgeLoc) -> QPointF:
        match loc.edge:
            case Edge.LEFT:
                return QPointF(0, loc.distance)
            case Edge.RIGHT:
                return QPointF(self.rect().width(), loc.distance)
            case Edge.TOP:
                return QPointF(loc.distance, 0)
            case Edge.BOTTOM:
                return QPointF(loc.distance, self.rect().height())
            case _:
                raise ValueError(f"Invalid edge: {loc.edge}")

    def loc2peri(self, loc: EdgeLoc) -> float:
        w = self._rect.width()
        h = self._rect.height()
        d = loc.distance
        if loc.edge == Edge.LEFT:
            return d
        elif loc.edge == Edge.BOTTOM:
            return w + d
        elif loc.edge == Edge.RIGHT:
            return w + h + (w - d)
        elif loc.edge == Edge.TOP:
            return w + h + w + (h - d)
        else:
            raise ValueError(f"Invalid edge: {loc.edge}")

    def peri2loc(self, peri: float) -> EdgeLoc:
        w = self._rect.width()
        h = self._rect.height()
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

    def locDelta(self : Self, loc1 : EdgeLoc, loc2 : EdgeLoc) -> float:
        w = self._rect.width()
        h = self._rect.height()
        p = 2 * (w + h)
        d = self.loc2peri(loc2) - self.loc2peri(loc1)
        if d >= 0: # CCW
            ccw_d = d % p
            cw_d = p - ccw_d
        else: # CW
            cw_d = -d % p
            ccw_d = p - cw_d
        return -cw_d if cw_d < ccw_d else ccw_d

    def locOffset(
        self   : Self,
        loc    : EdgeLoc,
        offset : float,
        corner : int
    ) -> EdgeLoc:
        w = self._rect.width()
        h = self._rect.height()
        def edgeLen(edge : Edge) -> float:
            return h if edge in [Edge.LEFT, Edge.RIGHT] else w
        def edgeNextCCW(edge : Edge) -> Edge:
            return \
                Edge.BOTTOM if edge == Edge.LEFT   else \
                Edge.RIGHT  if edge == Edge.BOTTOM else \
                Edge.TOP    if edge == Edge.RIGHT  else \
                Edge.LEFT   if edge == Edge.TOP    else \
                Edge.UNDEFINED
        def edgeNextCW(edge : Edge) -> Edge:
            return \
                Edge.TOP    if edge == Edge.LEFT   else \
                Edge.RIGHT  if edge == Edge.TOP    else \
                Edge.BOTTOM if edge == Edge.RIGHT  else \
                Edge.LEFT   if edge == Edge.BOTTOM else \
                Edge.UNDEFINED
        if offset >= 0: # CCW
            # convert EdgeLoc to EdgeLocCCW
            if loc.edge in [Edge.RIGHT, Edge.TOP]:
                loc.distance = edgeLen(loc.edge) - loc.distance
            # advance by offset
            while offset > 0:
                d = edgeLen(loc.edge) - loc.distance
                if d >= offset:
                    loc.distance += offset
                    offset = 0
                else:
                    offset -= d
                    loc.edge = edgeNextCCW(loc.edge)
                    loc.distance = 0
            # handle corner
            if loc.distance == edgeLen(loc.edge) and corner == +1:
                loc.edge = edgeNextCCW(loc.edge)
            # convert EdgeLocCCW to EdgeLoc
            if loc.edge in [Edge.RIGHT, Edge.TOP]:
                loc.distance = edgeLen(loc.edge) - loc.distance
        else: # CW
            # normalize offset
            offset = -offset
            # convert EdgeLoc to EdgeLocCW
            if loc.edge in [Edge.LEFT, Edge.BOTTOM]:
                loc.distance = edgeLen(loc.edge) - loc.distance
            # advance by offset
            while offset > 0:
                d = edgeLen(loc.edge) - loc.distance
                if d >= offset:
                    loc.distance += offset
                    offset = 0
                else:
                    offset -= d
                    loc.edge = edgeNextCW(loc.edge)
                    loc.distance = 0
            # handle corner
            if loc.distance == 0 and corner == -1:
                loc.edge = edgeNextCW(loc.edge)
            # convert EdgeLocCW to EdgeLoc
            if loc.edge in [Edge.LEFT, Edge.BOTTOM]:
                loc.distance = edgeLen(loc.edge) - loc.distance
        return loc

    def locOffset(
        self   : Self,
        loc    : EdgeLoc,
        offset : float,
        corner : int
    ) -> EdgeLoc:
        w = self._rect.width()
        h = self._rect.height()
        def edgeLen(edge : Edge) -> float:
            return h if edge in [Edge.LEFT, Edge.RIGHT] else w
        def edgeNextCCW(edge : Edge) -> Edge:
            return \
                Edge.BOTTOM if edge == Edge.LEFT   else \
                Edge.RIGHT  if edge == Edge.BOTTOM else \
                Edge.TOP    if edge == Edge.RIGHT  else \
                Edge.LEFT   if edge == Edge.TOP    else \
                Edge.UNDEFINED
        def edgeNextCW(edge : Edge) -> Edge:
            return \
                Edge.TOP    if edge == Edge.LEFT   else \
                Edge.RIGHT  if edge == Edge.TOP    else \
                Edge.BOTTOM if edge == Edge.RIGHT  else \
                Edge.LEFT   if edge == Edge.BOTTOM else \
                Edge.UNDEFINED
        loc = self.peri2loc(self.loc2peri(loc) + offset)
        if offset >= 0 and corner == +1: # CCW
            if (loc.edge in [Edge.LEFT, Edge.BOTTOM] and loc.distance == edgeLen(loc.edge)) \
            or (loc.edge in [Edge.RIGHT, Edge.TOP] and loc.distance == 0):
                loc.edge = edgeNextCCW(loc.edge)
                loc.distance = edgeLen(loc.edge) \
                    if loc.edge in [Edge.RIGHT, Edge.TOP] else 0
        elif offset < 0 and corner == -1: # CW
            if (loc.edge in [Edge.TOP, Edge.RIGHT] and loc.distance == edgeLen(loc.edge)) \
            or (loc.edge in [Edge.BOTTOM, Edge.LEFT] and loc.distance == 0):
                loc.edge = edgeNextCW(loc.edge)
                loc.distance = edgeLen(loc.edge) \
                    if loc.edge in [Edge.BOTTOM, Edge.LEFT] else 0
        return loc

    def ctxMenuAddPin(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        pass
