from typing import Self, overload
from math import sqrt, degrees, radians, sin, cos, atan2

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtGui     import QPainterPath, QColor

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
    _v1    : PolyVtx        # start vertex
    _v2    : PolyVtx        # end vertex
    _sweep : float          # arc sweep angle in degrees (-180..180), 0 = line
    _start : float | None   # calculated arc start angle, None for line
    _rect  : QRectF | None  # calculated arc rectangle, None for line

    def __init__(
        self   : Self,
        parent : "Polyline",
        v1     : PolyVtx,
        v2     : PolyVtx,
        sweep  : float = 0.0
    ) -> None:
        super().__init__(parent, QPointF(0, 0))
        self._v1 = v1
        self._v2 = v2
        self._sweep = sweep
        self.refresh()

    def refresh(self : Self) -> None:
        # set rotation to match chord angle
        vector = self._v2.pos() - self._v1.pos()
        self.setRotation(degrees(atan2(vector.y(), vector.x())))
        # handle line and arc cases
        if self._sweep == 0:  # line case
            self.setPos(self._chordMidpoint())
            self._rect = None
            self._start = None
        else:  # arc case
            # clamp sweep angle to -180..180
            self._sweep = max(-180, min(180, self._sweep))
            # vertex positions
            p1 = self._v1.pos()
            p2 = self._v2.pos()
            # chord
            chord_len = sqrt((p2.x() - p1.x())**2 + (p2.y() - p1.y())**2)
            if chord_len < 0.001:  # degenerate case
                self.setPos(p1)
                self._rect = QRectF(p1, QSizeF(0, 0))
                self._start = 0
                return
            chord_mid = QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)
            # radius: r = chord_len / (2 * sin(theta/2))
            half_sweep_rad = radians(abs(self._sweep) / 2)
            radius = chord_len / (2 * sin(half_sweep_rad))
            # calculate distance from chord midpoint to arc center
            # h = sqrt(r^2 - (chord/2)^2)
            h = sqrt(radius**2 - (chord_len / 2)**2)
            # calculate perpendicular direction to chord
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            # perpendicular to (dx, dy): rotate 90° = (-dy, dx)
            perp_x = -dy / chord_len
            perp_y = dx / chord_len
            # determine which side of chord the center is on
            # perpendicular (-dy, dx) points 90° CCW from chord
            # For negative sweep (CW), center is on the opposite side = subtract perp
            # For positive sweep (CCW), center is on the same side = add perp
            if self._sweep > 0:
                center = QPointF(chord_mid.x() + perp_x * h, chord_mid.y() + perp_y * h)
            else:
                center = QPointF(chord_mid.x() - perp_x * h, chord_mid.y() - perp_y * h)
            # create bounding rectangle for the arc circle
            self._rect = QRectF(
                center.x() - radius,
                center.y() - radius,
                2 * radius,
                2 * radius
            )
            # calculate start angle (angle from center to p1)
            self._start = degrees(atan2(p1.y() - center.y(), p1.x() - center.x()))
            print(f"Arc: sweep={self._sweep}, start={self._start}, p1={p1}, p2={p2}, center={center}, radius={radius}")
            # position segment grip at arc midpoint
            mid_angle_rad = radians(self._start + self._sweep / 2)
            arc_mid = QPointF(
                center.x() + radius * cos(mid_angle_rad),
                center.y() + radius * sin(mid_angle_rad)
            )
            self.setPos(arc_mid)

    def sweep(self : Self) -> float:
        """Get arc sweep angle in degrees: 0 = line, >0 = ccw arc, <0 = cw arc."""
        return self._sweep

    def setSweep(self : Self, angle : float) -> None:
        """Set arc sweep angle in degrees: 0 = line, >0 = ccw arc, <0 = cw arc."""
        self._sweep = angle
        self.refresh()

    def arcParams(self : Self) -> tuple[QRectF, float, float]:
        return self._rect, self._start, self._sweep

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
        # scale vertex grip positions
        scale_x = abs(x2-x1) / self.rect().width()
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
                if self._segments[i-1].sweep() == 0:
                    path.lineTo(v.pos())
                else:
                    path.arcTo(*self._segments[i-1].arcParams())
                v_prev = v.pos()
        if self._closed:
            path.closeSubpath()
        self.setPath(path)

    # temporary debug
    def paint(self, painter, option, widget) -> None:
        super().paint(painter, option, widget)
        painter.save()
        pen = painter.pen()
        pen.setWidthF(0)
        pen.setStyle(Qt.PenStyle.DashLine)
        for segment in self._segments:
            if segment.sweep() != 0:
                pen.setColor(QColor(Qt.GlobalColor.red))
                painter.setPen(pen)
                painter.drawLine(segment._v1.pos(), segment._v2.pos())
                pen.setColor(QColor(Qt.GlobalColor.yellow))
                painter.setPen(pen)
                painter.drawRect(segment._rect)
                print("--------------------------------")
                print("vertices:", segment._v1.pos(), segment._v2.pos())
                print("sweep:", segment.sweep())
                print("start:", segment._start)
                print("rect:", segment._rect)
        painter.restore()
