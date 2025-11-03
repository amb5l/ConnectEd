from typing import Self, overload
from math import sqrt, degrees, radians, sin, cos, atan2

from PyQt6.QtCore    import Qt, QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtGui     import QPainterPath, QColor

from ....app import logger

from ....core.utils import sign

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
    _ORIGIN_PATH_NAME = "Square"

    # instance attributes
    _index : int  # index of vertex

    def __init__(
        self   : Self,
        parent : "Polyline",
        index  : int,
        pos    : QPointF | None = None
    ) -> None:
        self._index = index
        super().__init__(parent, pos)

    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
        """Override to update path based on origin status."""
        if scene is not None:
            self._path_name = self._ORIGIN_PATH_NAME \
                if self._index == 0 else self._PATH_NAME
            self.setPath(scene.paths["Grip"][self._path_name])
            self.setVisible(True)

    def moveBy(self : Self, delta : QPointF) -> None:
        self.setPos(self.pos() + delta)
        parent : "Polyline" = self.parentItem()
        parent._updatePath()


class PolySeg(Grip):
    _PATH_NAME = "Arrow"

    # instance attributes
    _v1    : PolyVtx        # start vertex
    _v2    : PolyVtx        # end vertex
    _sweep : float  | None  # arc sweep angle (-180..180), +ve = CCW/RHS, None for line
    _start : float  | None  # calculated arc start angle, None for line
    _rect  : QRectF | None  # calculated arc rectangle, None for line

    def __init__(
        self   : Self,
        parent : "Polyline",
        v1     : PolyVtx,
        v2     : PolyVtx,
        sweep  : float | None = None
    ) -> None:
        super().__init__(parent, QPointF(0, 0))
        self._v1 = v1
        self._v2 = v2
        self._sweep = sweep
        self.refresh()

    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
        """Override to set path and visibility."""
        if scene is not None:
            self.setPath(scene.paths["Grip"][self._path_name])
            self.setVisible(True)

    def v1(self : Self) -> PolyVtx:
        return self._v1

    def setV1(self : Self, v1 : PolyVtx) -> None:
        self._v1 = v1
        self.refresh()

    def v2(self : Self) -> PolyVtx:
        return self._v2

    def setV2(self : Self, v2 : PolyVtx) -> None:
        self._v2 = v2
        self.refresh()

    def sweep(self : Self) -> float | None:
        """Get arc sweep angle in degrees: None = line, >0 = ccw arc, <0 = cw arc."""
        return self._sweep

    def setSweep(self : Self, angle : float | None) -> None:
        """Set arc sweep angle in degrees: None = line, >0 = ccw arc, <0 = cw arc."""
        self._sweep = angle
        self.refresh()

    def refresh(self : Self) -> None:
        # vertices
        x1 = self._v1.x()
        y1 = self._v1.y()
        x2 = self._v2.x()
        y2 = self._v2.y()
        # chord vector
        dx = x2 - x1
        dy = y2 - y1
        # set rotation to match chord angle
        self.setRotation(degrees(atan2(dy, dx)))
        # chord midpoint
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        # handle line and arc cases
        if self._sweep is None:  # line case
            self.setPos(mx, my)
            self._rect = None
            self._start = None
        else:  # arc case
            # clamp sweep angle to -180..180
            self._sweep = max(-180, min(180, self._sweep))
            # chord length
            d = sqrt(dx**2 + dy**2)
            if d < 0.001:  # degenerate case
                self.setPos(self._v1.pos())
                self._rect = QRectF(self._v1.pos(), QSizeF(0, 0))
                self._start = 0
                return
            # arc circle radius: r = chord_len / (2 * sin(theta/2))
            r = d / (2 * sin(radians(abs(self._sweep) / 2)))
            # chord midpoint to arc circle center distance
            # h = sqrt(r^2 - (chord/2)^2)
            h = sqrt(r**2 - (d / 2)**2)
            # calculate perpendicular unit vector
            ux = sign(self._sweep) *  dy / d
            uy = sign(self._sweep) * -dx / d
            # arc circle center
            cx = mx + (ux * h)
            cy = my + (uy * h)
            # arc circle bounding rect
            self._rect = QRectF(cx - r, cy - r, 2 * r, 2 * r)
            # calculate start angle
            c1x = x1 - cx
            c1y = y1 - cy
            self._start = degrees(atan2(-c1y, c1x))
            # position segment grip at arc midpoint
            a = radians(self._start + (self._sweep / 2))
            self.setPos(QPointF(cx + (r * cos(a)), cy - (r * sin(a))))

    def arcParams(self : Self) -> tuple[QRectF, float, float]:
        return self._rect, self._start, self._sweep


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

    def __init__(
        self     : Self,
        vertices : QPointF | list[QPointF],
        closed   : bool = False
    ) -> None:
        if isinstance(vertices, QPointF):
            vertices = [vertices]
        super().__init__()
        self.initItem()
        self.setPos(vertices[0])
        # initialize vertices and segments
        self._closed = False
        self._vertices = []
        self._segments = []
        for vertex in vertices:
            self.addVertex(vertex)
        self._buildSegments()
        # build path
        self._updatePath()
        self._sel_mode = 1  # Start in vertex-edit mode for interactive creation

    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
        """When added to scene, ensure all vertices and segments are initialized."""
        for vtx in self._vertices:
            vtx.onSceneChange(scene)
        for seg in self._segments:
            seg.onSceneChange(scene)

    def onSelectionChange(self : Self, selected : bool) -> None:
        if not selected:
            self._sel_mode = 0

    def selMode(self : Self) -> int:
        return self._sel_mode

    def setSelMode(self : Self, mode : int) -> None:
        self._sel_mode = mode
        scene : "DrawingScene" = self.scene()
        scene.updateGrips()

    def cycleSelMode(self : Self) -> None:
        self.setSelMode((self._sel_mode + 1) % 2)

    def vertexCount(self : Self) -> int:
        return len(self._vertices)

    def vertex(self : Self, index : int) -> PolyVtx:
        return self._vertices[index]

    def addVertex(self : Self, pos : QPointF) -> PolyVtx:
        """Add a new vertex."""
        vtx = PolyVtx(self, len(self._vertices), pos - self.pos())
        self._vertices.append(vtx)
        if self.vertexCount() > 1:
            self._segments.append(PolySeg(self, self._vertices[-2], vtx))
        self._updatePath()
        return vtx

    def removeLastVertex(self : Self) -> None:
        """Remove the last vertex."""
        seg = self._segments.pop()
        seg.setParentItem(None)
        vtx = self._vertices.pop()
        vtx.setParentItem(None)
        self._updatePath()

    def lastVertexPos(self : Self) -> QPointF:
        return self._vertices[-1].pos() + self.pos()

    def setLastVertexPos(self : Self, pos : QPointF) -> None:
        """Set position of last vertex."""
        self._vertices[-1].setPos(pos - self.pos())
        self._updatePath()

    def segment(self : Self, index : int) -> PolySeg:
        return self._segments[index]

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
        if len(self._vertices) < 2:  # degenerate case
            return
        for i in range(len(self._vertices) - 1):
            v1 = self._vertices[i]
            v2 = self._vertices[i+1]
            self._segments.append(PolySeg(self, v1, v2, None))
        if self._closed:
            self._segments.append(PolySeg(self, v2, self._vertices[0], None))

    def _updatePath(self : Self) -> None:
        """Rebuild path from vertices."""
        # adjust number of segments as required
        if len(self._segments) == len(self._vertices) - 1:
            if self._closed:
                # Add closing segment from last vertex to first vertex
                self._segments.append(PolySeg(
                    self, self._vertices[-1], self._vertices[0], None
                ))
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
                if self._segments[i-1].sweep() is None:
                    path.lineTo(v.pos())
                else:
                    path.arcTo(*self._segments[i-1].arcParams())
                v_prev = v.pos()
        if self._closed:
            path.closeSubpath()
        self.setPath(path)
