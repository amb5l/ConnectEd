from typing import Self, overload
from math import sqrt, degrees, radians, sin, cos, atan2

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtGui     import QPainterPath

from ....app import logger

from .base_rect import BaseRectangleMixin
from .grip      import Grip

from .mixin        import ItemMixin
from .mixin.pos    import ItemPosMixin
from .mixin.paint  import ItemPaintMixin
from .mixin.anchor import ItemRectAnchorPointsMixin
from .mixin.line   import ItemLineMixin
from .mixin.change import ItemChangeMixin
from .mixin.clone  import ItemCloneMixin
from .mixin.xml    import ItemXmlMixin
from .mixin.menu   import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene


class PolyVtx(Grip):
    _PATH_NAME = "Diamond"

    # instance attributes
    _index : int  # index of vertex/segment

    def __init__(
        self   : Self,
        parent : "Polyline",
        index  : int,
        pos    : QPointF | None = None
    ) -> None:
        super().__init__(parent, pos)
        self._index = index

    def moveBy(self : Self, delta : QPointF) -> None:
        self.setPos(self.pos() + delta)
        parent : "Polyline" = self.parentItem()
        parent._updatePath()


class PolySeg(Grip):
    _PATH_NAME = "Arrow"

    # instance attributes
    _v1        : PolyVtx  # start vertex
    _v2        : PolyVtx  # end vertex
    _arc_angle : float    # arc angle in degrees (0-180) (+ve = ccw, -ve = cw)
    _arc_rect  : QRectF   # arc rectangle
    _arc_start : float    # arc start angle in degrees
    _arc_sweep : float    # arc sweep angle in degrees

    def __init__(
        self   : Self,
        parent : "Polyline",
        v1     : PolyVtx,
        v2     : PolyVtx,
        arc    : int = 0
    ) -> None:
        super().__init__(parent, QPointF(0, 0))
        self._v1 = v1
        self._v2 = v2
        self._arc_angle = arc
        self.refresh()

    def refresh(self : Self) -> None:
        # set rotation to match chord angle
        vector = self._v2.pos() - self._v1.pos()
        self.setRotation(degrees(atan2(vector.y(), vector.x())))
        # handle line and arc cases
        if self._arc_angle == 0:  # line case
            # set position to midpoint of chord
            self.setPos(self._chordMidpoint())
        else:  # arc case
            # calculate arc parameters
            a = self._v1.pos()
            b = self._v2.pos()
            angle_deg = self._arc_angle
            chord_len = sqrt((a.x() - b.x())**2 + (a.y() - b.y())**2)
            if chord_len == 0 or abs(angle_deg) >= 360 or abs(angle_deg) == 0:
                return QRectF(), 0.0, 0.0
            abs_angle = abs(angle_deg)
            r = chord_len / (2 * sin(radians(abs_angle / 2)))
            h = sqrt(r**2 - (chord_len / 2)**2)
            mid = self._chordMidpoint()
            dir_ab = QPointF(b.x() - a.x(), b.y() - a.y())
            perp = QPointF(-dir_ab.y(), dir_ab.x()) / chord_len  # unit perp CCW
            if angle_deg < 0:
                perp = -perp  # flip side
            o = mid + perp * h
            self._arc_rect = QRectF(o.x() - r, o.y() - r, 2 * r, 2 * r)
            self._arc_start = degrees(atan2(a.y() - o.y(), a.x() - o.x()))
            self._arc_sweep = abs_angle if angle_deg > 0 else -abs_angle
            # # set position to midpoint of arc
            o = self._arc_rect.center()
            r = self._arc_rect.width() / 2  # assuming circular
            mid_angle = self._arc_start + self._arc_sweep / 2
            self.setPos(QPointF(
                o.x() + r * cos(radians(mid_angle)),
                o.y() + r * sin(radians(mid_angle))
            ))

    def arcAngle(self : Self) -> float:
        """Get arc angle in degrees: 0 = line, >0 = ccw arc, <0 = cw arc."""
        return self._arc_angle

    def setArcAngle(self : Self, angle : float) -> None:
        """Set arc angle in degrees: 0 = line, >0 = ccw arc, <0 = cw arc."""
        self._arc_angle = angle
        self.refresh()

    def arcParams(self : Self) -> tuple[QRectF, float, float]:
        return self._arc_rect, self._arc_start, self._arc_sweep

    def _chordMidpoint(self : Self) -> QPointF:
        """Calculate midpoint of chord."""
        return QPointF(
            (self._v1.pos().x() + self._v2.pos().x()) / 2,
            (self._v1.pos().y() + self._v2.pos().y()) / 2
        )


class Polyline(
    ItemMixin,
    ItemPosMixin,
    ItemPaintMixin,
    ItemRectAnchorPointsMixin,
    ItemLineMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    QGraphicsPathItem
):
    # instance attributes
    _vertices : list[PolyVtx]  # list of vertex grips
    _segments : list[PolySeg]  # list of segment grips
    _closed   : bool           # whether the polyline is closed (a polygon)
    _sel_mode : int            # current selection mode (0 = outline, 1 = vtx/seg)

    def __init__(self : Self, pos : QPointF) -> None:
        super().__init__()
        self.initItem()
        self.setPos(pos)
        # start open, with 2 vertices and 1 segment
        self._vertices = [
            PolyVtx(self, 0, QPointF(0, 0)),
            PolyVtx(self, 1, QPointF(0, 0))
        ]
        self._closed = False
        self._sel_mode = 0
        self._buildSegments()
        # update path
        self._updatePath()

    def onSelectionChange(self : Self, selected : bool) -> None:
        if not selected:
            self._sel_mode = 0

    def selMode(self : Self) -> int:
        return self._sel_mode

    def setSelMode(self : Self, mode : int) -> None:
        self._sel_mode = mode

    def vertexCount(self : Self) -> int:
        return len(self._vertices)

    def setLastVertexPos(self : Self, pos : QPointF) -> None:
        """Set position of last vertex. Note: pos is in local coordinates."""
        self._vertices[-1].setPos(pos)
        self._updatePath()

    def addVertex(self : Self, pos : QPointF) -> None:
        """Add a new vertex. Note: pos is in local coordinates."""
        vtx = PolyVtx(self, len(self._vertices), pos)
        self._vertices.append(vtx)
        self._segments.append(PolySeg(self, self._vertices[-2], vtx))
        self._updatePath()

    def removeLastVertex(self : Self) -> None:
        """Remove the last vertex."""
        self._segments.pop()
        self._vertices.pop()
        self._updatePath()

    def lastSegment(self : Self) -> PolySeg:
        return self._segments[-1]

    def closed(self : Self) -> bool:
        return self._closed

    def setClosed(self : Self, closed : bool) -> None:
        self._closed = closed
        self._updatePath()

    def anchorPointRect(self : Self) -> QRectF:
        return self.path().controlPointRect()

    def rect(self : Self) -> QRectF:
        return self.boundingRect()

    @overload
    def setPoints(
        self : Self,
        p1   : QPointF,
        p2   : QPointF
    ) -> None:
        ...

    @overload
    def setPoints(
        self : Self,
        x1   : float | int,
        y1   : float | int,
        x2   : float | int,
        y2   : float | int
    ) -> None:
        ...

    def setPoints(
        self : Self,
        p1_x1 : QPointF | float | int,
        p2_y1 : QPointF | float | int,
        x2    : float | int | None = None,
        y2    : float | int | None = None
    ) -> None:
        if x2 is None or y2 is None:
            x1 = p1_x1.x()
            y1 = p1_x1.y()
            x2 = p2_y1.x()
            y2 = p2_y1.y()
        else:
            x1 = p1_x1
            y1 = p2_y1
        final_pos = QPointF(
            x1 if x1 < x2 else x2,
            y1 if y1 < y2 else y2,
        )
        self.setPos(final_pos)
        scale_x = abs(x2-x1) / self.rect().width()
        # scale vertex grip positions
        scale_y = abs(y2-y1) / self.rect().height()
        for vertex in self._vertices:
            vertex.setPos(QPointF(
                vertex.pos().x() * scale_x, vertex.pos().y() * scale_y
            ))
        self._updatePath()

    def moveAnchorPointBy(self : Self, name : str, delta : QPointF) -> None:
        BaseRectangleMixin.moveAnchorPointBy(self, name, delta)

    def _buildSegments(self : Self) -> None:
        """Build segments from vertices. Default to lines not arcs."""
        self._segments = []
        for i in range(len(self._vertices) - 1):
            v1 = self._vertices[i]
            v2 = self._vertices[i+1]
            self._segments.append(PolySeg(self, v1, v2, 0))
        if self._closed:
            self._segments.append(PolySeg(self, v2, self._vertices[0], 0))

    def _updatePath(self : Self) -> None:
        """Rebuild path from vertices."""
        # adjust number of segments as required
        if len(self._segments) == len(self._vertices) - 1:
            if self._closed:
                self._segments.append(PolySeg(self, QPointF(0, 0)))
        elif len(self._segments) == len(self._vertices):
            if not self._closed:
                self._segments.pop()
        else:
            logger().warning(f"Invalid number of segments vs vertices: {len(self._segments)} vs {len(self._vertices)}")
            self._buildSegments()
        # update segments
        for segment in self._segments:
            segment.refresh()
        # build path
        path = QPainterPath()
        for i, v in enumerate(self._vertices):
            if i == 0:
                v_prev = v.pos()
                path.moveTo(v_prev)
            else:
                if self._segments[i-1].arcAngle() == 0:
                    path.lineTo(v.pos())
                else:
                    path.arcTo(*self._segments[i-1].arcParams())
                v_prev = v.pos()
        if self._closed:
            path.closeSubpath()
        self.setPath(path)
