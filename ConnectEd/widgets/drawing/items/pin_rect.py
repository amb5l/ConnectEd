from typing import Self, Optional

from PyQt6.QtCore    import QPointF, QSizeF

from . import EdgeLoc, Edge

from .port_pin import BasePin

from .base_rect import BaseRectangle, cmdPlaceBaseRectangle


class PinRect(BaseRectangle):
    def onGeometryChange(self : Self) -> None:
        super().onGeometryChange()
        # reposition pins
        for item in self.childItems():
            if isinstance(item, BasePin):
                item.onPositionChange()

    def getMenuItems(self : Self) -> list[str]:
        return ["Add Pin...", "-", "Appearance..."]

    def getEdgeLoc(
        self : Self,
        pos  : QPointF,
        snap : Optional[QPointF] = None
    ) -> EdgeLoc:
        def _snap(loc : EdgeLoc) -> EdgeLoc:
            e = loc.edge
            if snap is None:
                d = loc.distance
            elif loc.edge in [Edge.LEFT, Edge.RIGHT]:
                d = round(loc.distance / snap.x()) * snap.x()
            else:
                d = round(loc.distance / snap.y()) * snap.y()
            return EdgeLoc(e, d)
        centre_pos = self._rect.center() # always +ve (offset from top left)
        centre_lpos = self.pos() + centre_pos
        size = self._rect.size()
        w = size.width(); h = size.height()
        half_w = w / 2; half_h = h / 2
        # special case: centre
        if pos == centre_lpos:
            return _snap(EdgeLoc(Edge.LEFT, half_h))
        offset = pos - centre_lpos
        dx = offset.x(); dy = offset.y()
        # special case: zero width or height => capped linear distance
        if size.width() == 0 and size.height() != 0:
            edge = Edge.LEFT if dx <= 0 else Edge.RIGHT
            distance = min(max(half_h + dy, 0), h)
            return _snap(EdgeLoc(edge, distance))
        elif size.height() == 0 and size.width() != 0:
            edge = Edge.TOP if dy <= 0 else Edge.BOTTOM
            distance = min(max(half_w + dx, 0), w)
            return _snap(EdgeLoc(edge, distance))
        # special case: zero size
        if size == QSizeF(0, 0):
            if abs(dx) >= abs(dy):
                edge = Edge.LEFT if dx <= 0 else Edge.RIGHT
            else:
                edge = Edge.TOP if dy <= 0 else Edge.BOTTOM
            return EdgeLoc(edge, 0)
        # get edge (quadrant)
        if dx == 0:
            is_vertical = False
        elif dy == 0:
            is_vertical = True
        elif (h >= w):  # true for tall or square:
            is_vertical = (abs(dx / dy) >= abs(w / h))
        else:  # wide: flip for = case
            is_vertical = (abs(dx / dy) > abs(w / h))
        if is_vertical:
            edge = Edge.LEFT if dx < 0 else Edge.RIGHT
        else:
            edge = Edge.TOP if dy < 0 else Edge.BOTTOM
        # get distance
        if edge in [Edge.LEFT, Edge.RIGHT]:
            scaled_dy = dy * abs(half_w/ dx)
            distance = half_h + scaled_dy
        elif edge in [Edge.TOP, Edge.BOTTOM]:
            scaled_dx = dx * abs(half_h / dy)
            distance = half_w + scaled_dx
        return _snap(EdgeLoc(edge, distance))

    def getEdgeLocPos(self : Self, loc : EdgeLoc) -> QPointF:
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

class cmdPlacePinRect(cmdPlaceBaseRectangle):
    element : PinRect
