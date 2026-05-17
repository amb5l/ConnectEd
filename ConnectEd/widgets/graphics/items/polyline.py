from typing import Self, overload

from PyQt6.QtCore    import QPointF, QRectF, \
                            QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsPathItem, QMenu
from PyQt6.QtGui     import QAction

from ....app import logger

from ....core.check import checked
from ....core.defs  import PITCH
from ....core.types import DataKind, RectHandleId
from ....core.xml   import fromXmlAttrs

from ...dialogs.arc import ArcDialog

from ..properties import InherentProperty, PropertiesMixin

from ..painter_path import PainterPath

from .handle import HandleGripKind
from .grip   import VertexGripItem, SegmentGripItem

from .mixin           import ItemMixin
from .mixin.transform import ItemTransformMixin
from .mixin.paint     import ItemPaintMixin
from .mixin.handle    import ItemRectHandlesMixin
from .mixin.line      import ItemLineMixin
from .mixin.change    import ItemChangeMixin
from .mixin.clone     import ItemCloneMixin
from .mixin.xml       import ItemXmlMixin
from .mixin.menu      import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene
    from ..views.drawing  import DrawingView


class PolyVtxItem(VertexGripItem):
    # instance attributes
    _index : int  # index of vertex

    @checked
    def __init__(
        self   : Self,
        parent : "PolylineItem",
        index  : int,
        pos    : QPointF | None = None
    ) -> None:
        self._index = index
        super().__init__(parent, pos)

    @checked
    def index(self : Self) -> int:
        return self._index

    @checked
    def moveBy(self : Self, delta : QPointF) -> None:
        parent : "PolylineItem" = self.parentItem()
        if self.index() == 0 and parent.selMode() == 0:
            parent.setPos(parent.pos() + delta)
        else:
            self.setPos(self.pos() + delta)
            parent.updatePath()

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        items = []
        return items

    @checked
    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__.removesuffix("Item"))
        xw.writeAttribute("X", str(self.pos().x()))
        xw.writeAttribute("Y", str(self.pos().y()))
        xw.writeEndElement()


class PolySegItem(SegmentGripItem):
    # instance attributes
    _v1    : PolyVtxItem   # start vertex
    _v2    : PolyVtxItem   # end vertex
    _sweep : float | None  # arc sweep angle (-180..180), +ve = CCW/RHS, None for line

    @checked
    def __init__(
        self   : Self,
        parent : "PolylineItem",
        v1     : PolyVtxItem,
        v2     : PolyVtxItem,
        sweep  : float | None = None
    ) -> None:
        super().__init__(parent, QPointF(0, 0))
        self._v1 = v1
        self._v2 = v2
        self._sweep = sweep

    @checked
    def v1(self : Self) -> PolyVtxItem:
        return self._v1

    @checked
    def setV1(self : Self, v1 : PolyVtxItem) -> None:
        self._v1 = v1

    @checked
    def v2(self : Self) -> PolyVtxItem:
        return self._v2

    @checked
    def setV2(self : Self, v2 : PolyVtxItem) -> None:
        self._v2 = v2

    @checked
    def sweep(self : Self) -> float | None:
        return self._sweep

    @checked
    def setSweep(self : Self, angle : float | None) -> None:
        self._sweep = angle

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        items = []
        a = self.sweep()
        items.append(view.action("Line", self._toLine, a is None))
        a_text = f" ({a}°)" if a is not None else ""
        items.append(view.action(
            f"Arc{a_text}...", lambda: self._toArc(view), a is not None
        ))
        return items

    @checked
    def _toLine(self : Self) -> None:
        if self.sweep() is None:
            return
        scene : "DrawingScene" = self.scene()
        scene.editPolySeg(self, None, undoable=True)

    @checked
    def _toArc(self : Self, view : "DrawingView") -> None:
        dialog = ArcDialog(self.sweep(), view)
        if dialog.exec():
            scene : "DrawingScene" = self.scene()
            scene.editPolySeg(self, dialog.getAngle(), undoable=True)


class PolylineItem(
    ItemMixin,
    ItemTransformMixin,
    ItemPaintMixin,
    ItemRectHandlesMixin,
    ItemLineMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin,
    QGraphicsPathItem
):
    # class attributes
    _RESIZE_HANDLE_GRIP_KIND = HandleGripKind.POLYLINE
    _PROPERTIES = \
        {
            "Closed" : InherentProperty(
                kind   = DataKind.BOOL,
                getter = lambda self: self.closed(),
                setter = lambda self, value: self.setClosed(value)
            )
        } | \
        ItemTransformMixin._PROPERTIES_POS | \
        ItemTransformMixin._PROPERTIES_ROTATE | \
        ItemLineMixin._PROPERTIES_LINE

    # instance attributes
    _vertices : list[PolyVtxItem]  # list of vertex grips
    _segments : list[PolySegItem]  # list of segment grips
    _closed   : bool               # whether the polyline is closed (a polygon)
    _sel_mode : int                # current selection mode (0 = outline, 1 = vtx/seg)

    @checked
    def __init__(
        self     : Self,
        pos      : QPointF | None = None,
        vertices : list[QPointF] | None = None,
        closed   : bool = False,
        fresh    : bool = True
    ) -> None:
        super().__init__()
        self.initItem(fresh)
        self.setPos(pos or QPointF())
        # initialize vertices and segments
        self._vertices = []
        self._segments = []
        self._closed = closed
        self.addVertex(self.pos())  # origin vertex (always at local (0,0))
        for vertex in vertices or []:
            self.addVertex(vertex)
        self._buildSegments()
        # build path
        self.updatePath()
        self._sel_mode = 1  # Start in vertex-edit mode for interactive creation

    @checked
    def onSceneChanged(self : Self, scene : "DrawingScene | None") -> None:
        """Initialize vertices, segments, and APs on scene change."""
        for vtx in self._vertices:
            vtx.onSceneChanged(scene)
        for seg in self._segments:
            seg.onSceneChanged(scene)
        if hasattr(self, '_handles'):
            for h in self._handles.values():
                h._grip.onSceneChanged(scene)

    @checked
    def onSelectionChange(self : Self, selected : bool) -> None:
        if not selected:
            self._sel_mode = 0

    @checked
    def selMode(self : Self) -> int:
        return self._sel_mode

    @checked
    def setSelMode(self : Self, mode : int) -> None:
        self._sel_mode = mode
        scene : "DrawingScene" = self.scene()
        scene.updateGrips()

    @checked
    def cycleSelMode(self : Self) -> None:
        self.setSelMode((self._sel_mode + 1) % 2)

    @checked
    def vertices(self : Self) -> list[PolyVtxItem]:
        return self._vertices

    @checked
    def vertexCount(self : Self) -> int:
        return len(self._vertices)

    @checked
    def vertex(self : Self, index : int) -> PolyVtxItem:
        return self._vertices[index]

    @checked
    def addVertex(
        self   : Self,
        pos   : QPointF | None = None,
        sweep : float | None = None
    ) -> PolyVtxItem:
        """Add a new vertex."""
        vtx = PolyVtxItem(self, len(self._vertices), pos - self.pos())
        self._vertices.append(vtx)
        if self.vertexCount() > 1:
            self._segments.append(PolySegItem(self, self._vertices[-2], vtx, sweep))
        self.updatePath()
        return vtx

    @checked
    def delLastVertex(self : Self) -> None:
        """Delete the last vertex."""
        seg = self._segments.pop()
        seg.setParentItem(None)
        vtx = self._vertices.pop()
        vtx.setParentItem(None)
        self.updatePath()

    @checked
    def lastVertexPos(self : Self) -> QPointF:
        return self._vertices[-1].pos() + self.pos()

    @checked
    def setLastVertexPos(self : Self, pos : QPointF) -> None:
        """Set position of last vertex."""
        self._vertices[-1].setPos(pos - self.pos())
        self.updatePath()

    @checked
    def segment(self : Self, index : int) -> PolySegItem:
        return self._segments[index]

    @checked
    def lastSegment(self : Self) -> PolySegItem:
        return self._segments[-1]

    @checked
    def closed(self : Self) -> bool:
        return self._closed

    @checked
    def setClosed(self : Self, closed : bool) -> None:
        self._closed = closed
        self.updatePath()

    @checked
    def close(self : Self, sweep : float | None = None) -> None:
        self._segments.append(PolySegItem(
            self, self._vertices[-1], self._vertices[0], sweep
        ))
        self.setClosed(True)

    @checked
    def open(self : Self) -> None:
        seg = self._segments.pop()
        seg.setParentItem(None)
        self.setClosed(False)

    @checked
    def handleRect(self : Self) -> QRectF:
        return self.rect()

    @checked
    def rect(self : Self) -> QRectF:
        return self.path().controlPointRect()

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

    @checked
    def setPoints(
        self : Self,
        p1_x1 : QPointF | float | int,
        p2_y1 : QPointF | float | int,
        x2    : float | int | None = None,
        y2    : float | int | None = None
    ) -> None:
        # normalise arguments
        if x2 is None or y2 is None:
            x1 = p1_x1.x()
            y1 = p1_x1.y()
            x2 = p2_y1.x()
            y2 = p2_y1.y()
        else:
            x1 = p1_x1
            y1 = p2_y1
        # x1,y1 = top left; x2,y2 = bottom right
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        # new width and height (minimum = PITCH)
        new_w = max(x2 - x1, PITCH)
        new_h = max(y2 - y1, PITCH)
        # current rect in item coordinates
        r = self.rect()
        rx, ry = r.x(), r.y()
        old_w = max(r.width(), PITCH)
        old_h = max(r.height(), PITCH)
        scale_x = new_w / old_w
        scale_y = new_h / old_h
        # offset vertices relative to rect top-left, then scale
        for vertex in self._vertices:
            vertex.setPos(QPointF(
                (vertex.pos().x() - rx) * scale_x,
                (vertex.pos().y() - ry) * scale_y
            ))
        # re-base so vertex 0 is back at (0,0); adjust pos to compensate
        v0 = QPointF(self._vertices[0].pos())
        self.setPos(QPointF(x1 + v0.x(), y1 + v0.y()))
        for vertex in self._vertices:
            vertex.setPos(vertex.pos() - v0)
        self.updatePath()

    @checked
    def moveHandleBy(self : Self, id : RectHandleId, d : QPointF) -> None:
        """Resize bbox from handles; mixin assumes rect top-left at item (0,0)."""
        p1 = self.mapToParent(self.rect().topLeft())
        p2 = self.mapToParent(self.rect().bottomRight())
        match id:
            case RectHandleId.TOP_LEFT:
                self.setPoints(p1 + d, p2)
            case RectHandleId.TOP_CENTER:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x(), p2.y())
            case RectHandleId.TOP_RIGHT:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x() + d.x(), p2.y())
            case RectHandleId.MIDDLE_LEFT:
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y())
            case RectHandleId.MIDDLE_CENTER:
                self.moveBy(d)
            case RectHandleId.MIDDLE_RIGHT:
                self.setPoints(p1.x(), p1.y(), p2.x() + d.x(), p2.y())
            case RectHandleId.BOTTOM_LEFT:
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y() + d.y())
            case RectHandleId.BOTTOM_CENTER:
                self.setPoints(p1.x(), p1.y(), p2.x(), p2.y() + d.y())
            case RectHandleId.BOTTOM_RIGHT:
                self.setPoints(p1, p2 + d)
            case _:
                raise ValueError(f"Invalid handle: {id}")

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        items = []
        return items

    @checked
    def updatePath(self : Self) -> None:
        """Rebuild path from vertices."""
        # adjust number of segments as required
        if len(self._segments) == len(self._vertices) - 1:
            if self._closed:
                # Add closing segment from last vertex to first vertex
                self._segments.append(PolySegItem(
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
        # update handles
        if hasattr(self, '_handles'):
            self.updateHandlePositions()

    @checked
    def _buildSegments(self : Self) -> None:
        """Build segments from vertices. Default to lines not arcs."""
        self._segments = []
        if len(self._vertices) < 2:  # degenerate case
            return
        for i in range(len(self._vertices) - 1):
            v1 = self._vertices[i]
            v2 = self._vertices[i+1]
            self._segments.append(PolySegItem(self, v1, v2, None))
        if self._closed:
            self._segments.append(PolySegItem(self, v2, self._vertices[0], None))

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self.toXmlBegin(xw)
        self.toXmlAttrs(xw)
        # serialise segments
        for i, vtx in enumerate(self._vertices[1:]):
            seg = self._segments[i-1]
            xw.writeStartElement("Segment")
            x = vtx.pos().x()
            x = int(x) if x.is_integer() else x
            xw.writeAttribute("X", str(x))
            y = vtx.pos().y()
            y = int(y) if y.is_integer() else y
            xw.writeAttribute("Y", str(y))
            sweep = seg.sweep()
            if sweep is not None and sweep != 0:
                sweep = int(sweep) if sweep.is_integer() else sweep
                xw.writeAttribute("Sweep", str(sweep))
            xw.writeEndElement()
            pass
        self.toXmlEnd(xw)

    @checked
    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        xml_item_name = cls.__name__.removesuffix("Item")
        instance : "PolylineItem" = cls(fresh=False)
        fromXmlAttrs(instance, xr)
        # deserialise segments
        while not (xr.isEndElement() and xr.name() == xml_item_name):
            if xr.isStartElement():
                item_name = xr.name()
                if item_name == "Segment":
                    xml_attrs = xr.attributes()
                    x = None
                    y = None
                    sweep = None
                    for xml_attr in xml_attrs:
                        match xml_attr.name():
                            case "X":
                                x = float(xml_attr.value())
                            case "Y":
                                y = float(xml_attr.value())
                            case "Sweep":
                                sweep = float(xml_attr.value())
                            case _:
                                logger().warning(
                                    f"Unexpected attribute: {xml_attr.name()}"
                                )
                    if x is not None and y is not None:
                        # XML stores local coords (relative to polyline origin);
                        # addVertex expects parent coords.
                        instance.addVertex(QPointF(x, y) + instance.pos(), sweep)
                else:
                    logger().warning(f"Unexpected element: {item_name}")
            xr.readNext()
        return instance

class SymbolPolylineItem(PolylineItem):
    pass
