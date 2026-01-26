from typing import Self, overload

from PyQt6.QtCore    import QPointF, QRectF, \
                            QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsPathItem, QMenu
from PyQt6.QtGui     import QAction

from ....app import logger

from ....core.xml import fromXmlAttrs

from ...dialogs.arc import ArcDialog

from ..property   import PropertySpec
from ..properties import PropertiesMixin

from ..painter_path import PainterPath

from .base_rect import BaseRectangleMixin
from .grip      import GripItem

from .mixin        import ItemMixin
from .mixin.pos    import ItemPosMixin
from .mixin.rotate import ItemRotateMixin
from .mixin.paint  import ItemPaintMixin
from .mixin.handle import ItemRectHandlesMixin
from .mixin.line   import ItemLineMixin
from .mixin.change import ItemChangeMixin
from .mixin.clone  import ItemCloneMixin
from .mixin.xml    import ItemXmlMixin
from .mixin.menu   import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene
    from ..views.drawing  import DrawingView


class PolyVtxItem(GripItem):
    _PATH_NAME = "Diamond"
    _ORIGIN_PATH_NAME = "Square"

    # instance attributes
    _index : int  # index of vertex

    def __init__(
        self   : Self,
        parent : "PolylineItem",
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
        parent : "PolylineItem" = self.parentItem()
        parent.updatePath()

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        items = []
        return items

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__)
        xw.writeAttribute("X", str(self.pos().x()))
        xw.writeAttribute("Y", str(self.pos().y()))
        xw.writeEndElement()


class PolySegItem(GripItem):
    _PATH_NAME = "Arrow"

    # instance attributes
    _v1    : PolyVtxItem        # start vertex
    _v2    : PolyVtxItem        # end vertex
    _sweep : float  | None  # arc sweep angle (-180..180), +ve = CCW/RHS, None for line

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

    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
        """Override to set path and visibility."""
        if scene is not None:
            self.setPath(scene.paths["Grip"][self._path_name])
            self.setVisible(True)

    def v1(self : Self) -> PolyVtxItem:
        return self._v1

    def setV1(self : Self, v1 : PolyVtxItem) -> None:
        self._v1 = v1

    def v2(self : Self) -> PolyVtxItem:
        return self._v2

    def setV2(self : Self, v2 : PolyVtxItem) -> None:
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


class PolylineItem(
    ItemMixin,
    ItemPosMixin,
    ItemRotateMixin,
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
    _INHERENT_PROPERTIES = \
        {
            "Closed" : PropertySpec(
                kind   = "bool",
                getter = lambda self: self.closed(),
                setter = lambda self, value: self.setClosed(value)
            )
        } | \
        ItemPosMixin._INHERENT_PROPERTIES_POS | \
        ItemRotateMixin._INHERENT_PROPERTIES_ROTATE | \
        ItemLineMixin._INHERENT_PROPERTIES_LINE

    # instance attributes
    _vertices : list[PolyVtxItem]  # list of vertex grips
    _segments : list[PolySegItem]  # list of segment grips
    _closed   : bool           # whether the polyline is closed (a polygon)
    _sel_mode : int            # current selection mode (0 = outline, 1 = vtx/seg)

    def __init__(
        self     : Self,
        pos      : QPointF | None = None,
        vertices : list[QPointF] = [],
        closed   : bool = False,
        bare     : bool = False
    ) -> None:
        super().__init__()
        self.initItem(bare=bare)
        self.setPos(pos or QPointF())
        # initialize vertices and segments
        self._vertices = []
        self._segments = []
        self._closed = closed
        self.addVertex(pos)  # origin vertex
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
        if hasattr(self, '_handles'):
            for h in self._handles.values():
                h._grip.onSceneChange(scene)

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

    def vertex(self : Self, index : int) -> PolyVtxItem:
        return self._vertices[index]

    def addVertex(self : Self, pos : QPointF, sweep : float | None = None) -> PolyVtxItem:
        """Add a new vertex."""
        vtx = PolyVtxItem(self, len(self._vertices), pos - self.pos())
        print("addVertex:", vtx._index, vtx.pos())
        self._vertices.append(vtx)
        if self.vertexCount() > 1:
            self._segments.append(PolySegItem(self, self._vertices[-2], vtx, sweep))
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

    def segment(self : Self, index : int) -> PolySegItem:
        return self._segments[index]

    def lastSegment(self : Self) -> PolySegItem:
        return self._segments[-1]

    def closed(self : Self) -> bool:
        return self._closed

    def setClosed(self : Self, closed : bool) -> None:
        self._closed = closed
        self.updatePath()

    def close(self : Self, sweep : float | None = None) -> None:
        self._segments.append(PolySegItem(
            self, self._vertices[-1], self._vertices[0], sweep
        ))
        self.setClosed(True)

    def open(self : Self) -> None:
        seg = self._segments.pop()
        seg.setParentItem(None)
        self.setClosed(False)

    def handleRect(self : Self) -> QRectF:
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

    def moveHandleBy(self : Self, name : str, delta : QPointF) -> None:
        BaseRectangleMixin.moveHandleBy(self, name, delta)

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        items = []
        return items

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

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        instance : "PolylineItem" = cls(bare=True)
        fromXmlAttrs(instance, xr)
        # deserialise segments
        while not (xr.isEndElement() and xr.name() == cls.__name__):
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
                                logger().warning(f"Unexpected attribute: {xml_attr.name()}")
                    if x is not None and y is not None:
                        instance.addVertex(QPointF(x, y), sweep)
                else:
                    logger().warning(f"Unexpected element: {item_name}")
            xr.readNext()
        return instance

class SymbolPolylineItem(PolylineItem):
    pass
