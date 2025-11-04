from typing import Self, overload

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsPathItem, QMenu
from PyQt6.QtGui     import QAction

from ....app import logger

from ...dialogs.arc import ArcDialog

from ..painter_path import PainterPath

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
    from ..views.drawing import DrawingView


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
        parent.updatePath()

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        items = []
        return items


class PolySeg(Grip):
    _PATH_NAME = "Arrow"

    # instance attributes
    _v1    : PolyVtx        # start vertex
    _v2    : PolyVtx        # end vertex
    _sweep : float  | None  # arc sweep angle (-180..180), +ve = CCW/RHS, None for line

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

    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
        """Override to set path and visibility."""
        if scene is not None:
            self.setPath(scene.paths["Grip"][self._path_name])
            self.setVisible(True)

    def v1(self : Self) -> PolyVtx:
        return self._v1

    def setV1(self : Self, v1 : PolyVtx) -> None:
        self._v1 = v1

    def v2(self : Self) -> PolyVtx:
        return self._v2

    def setV2(self : Self, v2 : PolyVtx) -> None:
        self._v2 = v2

    def sweep(self : Self) -> float | None:
        return self._sweep

    def setSweep(self : Self, angle : float | None) -> None:
        self._sweep = angle

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        items = []
        a = self.sweep()
        items.append(view.action("Line", self._toLine, a is None))
        a_text = f" ({a}°)" if a is not None else ""
        items.append(view.action(
            f"Arc{a_text}...", lambda: self._toArc(view), a is not None
        ))
        return items

    def _toLine(self : Self) -> None:
        if self.sweep() is None:
            return
        scene : "DrawingScene" = self.scene()
        scene.editPolySeg(self, None, undoable=True)

    def _toArc(self : Self, view : "DrawingView") -> None:
        dialog = ArcDialog(self.sweep(), view)
        if dialog.exec():
            scene : "DrawingScene" = self.scene()
            scene.editPolySeg(self, dialog.getAngle(), undoable=True)

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
        self.updatePath()
        self._sel_mode = 1  # Start in vertex-edit mode for interactive creation

    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
        """Initialize vertices, segments, and APs on scene change."""
        for vtx in self._vertices:
            vtx.onSceneChange(scene)
        for seg in self._segments:
            seg.onSceneChange(scene)
        if hasattr(self, '_anchor_points'):
            for ap in self._anchor_points.values():
                ap._grip.onSceneChange(scene)

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

    def addVertex(self : Self, pos : QPointF, sweep : float | None = None) -> PolyVtx:
        """Add a new vertex."""
        vtx = PolyVtx(self, len(self._vertices), pos - self.pos())
        self._vertices.append(vtx)
        if self.vertexCount() > 1:
            self._segments.append(PolySeg(self, self._vertices[-2], vtx, sweep))
        self.updatePath()
        return vtx

    def removeLastVertex(self : Self) -> None:
        """Remove the last vertex."""
        seg = self._segments.pop()
        seg.setParentItem(None)
        vtx = self._vertices.pop()
        vtx.setParentItem(None)
        self.updatePath()

    def lastVertexPos(self : Self) -> QPointF:
        return self._vertices[-1].pos() + self.pos()

    def setLastVertexPos(self : Self, pos : QPointF) -> None:
        """Set position of last vertex."""
        self._vertices[-1].setPos(pos - self.pos())
        self.updatePath()

    def segment(self : Self, index : int) -> PolySeg:
        return self._segments[index]

    def lastSegment(self : Self) -> PolySeg:
        return self._segments[-1]

    def closed(self : Self) -> bool:
        return self._closed

    def setClosed(self : Self, closed : bool) -> None:
        self._closed = closed
        self.updatePath()

    def close(self : Self, sweep : float | None = None) -> None:
        self._segments.append(PolySeg(
            self, self._vertices[-1], self._vertices[0], sweep
        ))
        self.setClosed(True)

    def open(self : Self) -> None:
        seg = self._segments.pop()
        seg.setParentItem(None)
        self.setClosed(False)

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
        self.updatePath()

    def moveAnchorPointBy(self : Self, name : str, delta : QPointF) -> None:
        BaseRectangleMixin.moveAnchorPointBy(self, name, delta)

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        items = []
        return items

    def updatePath(self : Self) -> None:
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
            logger().warning(
                f"Invalid number of segments vs vertices: "
                f"{len(self._segments)} vs {len(self._vertices)}"
            )
            self._buildSegments()
        # build path
        path = PainterPath()
        for i, v in enumerate(self._vertices):
            if i == 0:
                v_prev = v.pos()
                path.moveTo(v_prev)
            else:
                if self._segments[i-1].sweep() is None:
                    path.lineTo(v.pos())
                else:
                    path.arcSpanTo(v.pos(), self._segments[i-1].sweep())
                self._segments[i-1].setPos(path.currentMidPos())
                self._segments[i-1].setRotation(path.currentAngle())
                v_prev = v.pos()
        # handle closed case
        if self._closed:
            if self._segments[-1].sweep() is None:
                path.lineTo(self._vertices[0].pos())
            else:
                path.arcSpanTo(self._vertices[0].pos(), self._segments[-1].sweep())
            self._segments[-1].setPos(path.currentMidPos())
            self._segments[-1].setRotation(path.currentAngle())
            path.closeSubpath()
        # update path
        self.setPath(path)
        # update anchor points
        if hasattr(self, '_anchor_points'):
            self.updateAnchorPoints()

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