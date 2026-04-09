import networkx

from typing import Self
from dataclasses import dataclass

from PyQt6.QtCore import Qt, QPointF, QRectF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtGui  import QPainter, QPen, QBrush

from .....app import settings, logger

from .....core.types import DataKind
from .....core.xml   import toXmlAttrs, fromXmlAttrs

from ...properties import InherentProperty

from ...items.node    import NodeItem
from ...items.entry   import EntryItem
from ...items.vertex  import VertexItem
from ...items.segment import SegmentItem

from ...items.mixin.xml import ItemXmlMixin

from ..drawing import DrawingScene

from ..drawing.cmd import cmdExec

from .api       import DiagramSceneApiMixin
from .resources import DiagramSceneResourcesMixin

from .cmd.conn import CmdAddSegment

from .netlist import Netlist


@dataclass
class DiagramSheet:
    name : str
    rect : QRectF


class DiagramScene(
    DiagramSceneResourcesMixin,
    DiagramSceneApiMixin,
    DrawingScene
):
    # class attributes
    _PROPERTIES = DrawingScene._PROPERTIES | {
        "Sheet Name" : InherentProperty(
            kind   = DataKind.STR,
            getter = lambda self: self.getSheetName(),
            setter = lambda self, value: self.setSheetName(value)
        ),
        "Sheet Width" : InherentProperty(
            kind   = DataKind.FLOAT,
            getter = lambda self: self.getSheetWidth(),
            setter = lambda self, value: self.setSheetWidth(value)
        ),
        "Sheet Height" : InherentProperty(
            kind   = DataKind.FLOAT,
            getter = lambda self: self.getSheetHeight(),
            setter = lambda self, value: self.setSheetHeight(value)
        ),
        "Margin" : InherentProperty(
            kind   = DataKind.FLOAT,
            getter = lambda self: self.margin,
            setter = lambda self, value: self.setMargin(value)
        ),
        "Border" : InherentProperty(
            kind   = DataKind.FLOAT,
            getter = lambda self: self.border,
            setter = lambda self, value: self.setBorder(value)
        )
    }

    # instance attributes
    sheet   : DiagramSheet
    margin  : float           # distance from paper edge to border line
    border  : float           # line width
    netlist : Netlist


    def __init__(self : Self, fresh : bool = True) -> None:
        sheet_name = settings().get("defaults/sheet/name")
        sheet_size = settings().get("defaults/sheet/size")
        sheet_rect = QRectF(QPointF(0, 0), sheet_size)
        self.sheet = DiagramSheet(sheet_name, sheet_rect)
        self.margin = settings().get("defaults/margin")
        self.border = settings().get("defaults/border")
        super().__init__(sheet_size, fresh)
        self.netlist = Netlist()

    def updateSceneRect(self : Self, rect : QRectF | None = None) -> None:
        super().updateSceneRect(self.sheet.rect)  # sheet is minimum rect

    def drawBackground(self : Self, painter : QPainter, rect : QRectF) -> None:
        painter.fillRect(rect, settings().get("theme/background"))
        painter.fillRect(
            self.sheet.rect,
            settings().get("theme/sheet")
        )
        painter.setPen(QPen(
            settings().get("theme/border"),
            self.border,
            Qt.PenStyle.SolidLine
        ))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawRect(self.sheet.rect.adjusted(
            self.margin, self.margin, -self.margin, -self.margin
        ))

    def getSheetName(self : Self) -> str:
        return self.sheet.name

    def setSheetName(self : Self, name : str) -> None:
        self.sheet.name = name

    def getSheetWidth(self : Self) -> float:
        return self.sheet.rect.width()

    def setSheetWidth(self : Self, width : float) -> None:
        self.sheet.rect.setWidth(width)
        self.updateSceneRect()
        self.update()

    def getSheetHeight(self : Self) -> float:
        return self.sheet.rect.height()

    def setSheetHeight(self : Self, height : float) -> None:
        self.sheet.rect.setHeight(height)
        self.updateSceneRect()
        self.update()

    def getMargin(self : Self) -> float:
        return self.margin

    def setMargin(self : Self, margin : float) -> None:
        self.margin = margin
        self.update()

    def getBorder(self : Self) -> float:
        return self.border

    def setBorder(self : Self, border : float) -> None:
        self.border = border
        self.update()

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        # start
        xw.writeStartElement(self.__class__.__name__.replace("Scene", ""))
        # properties
        toXmlAttrs(self, xw)
        # items: must be top level (unparented); exclude vertices and segments
        for item in self.items():
            if isinstance(item, NodeItem | SegmentItem):
                continue
            if item.parentItem() is None:
                if isinstance(item, ItemXmlMixin):
                    item.toXml(xw)
                else:
                    logger().warning(f"Unexpected item: {item.type()}")
        # entries, vertices and PropertyLabelItem instances
        raw_nodes : list[VertexItem] = list(self.netlist.vertices())
        entries : list[EntryItem] = [
            node for node in raw_nodes \
                if isinstance(node, EntryItem)
        ]
        vertices : list[VertexItem] = [
            node for node in raw_nodes \
                if isinstance(node, VertexItem) \
                    and not isinstance(node, EntryItem)
        ]
        nodes = entries + vertices  # entries then vertices
        for id, node in enumerate(raw_nodes):
            node.toXml(xw, id)
        # segments
        for component in networkx.connected_components(self._graph):
            subgraph = self._graph.subgraph(component)
            pairs = [
                f"{nodes.index(v1)},{nodes.index(v2)}"
                     for v1, v2 in subgraph.edges()
            ]
            xw.writeStartElement("PhysicalNet")
            xw.writeAttribute("Edges", " ".join(pairs))
            xw.writeEndElement()
        # done
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        from ...items import _item_classes
        nodes : list["NodeItem | None"] = []
        top_element_name = cls.__name__.replace("Scene", "")
        if xr.name() != top_element_name:
            raise ValueError(f"Expected {top_element_name} element, got {xr.name()}")
        scene : DrawingScene = cls()
        fromXmlAttrs(scene, xr)
        while not (xr.isEndElement() and xr.name() == top_element_name):
            if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                element_name = xr.name()
                item_name = element_name + "Item"
                if element_name in ["Entry", "Vertex"]:
                    node_id = int(xr.attributes().value("ID"))
                    if element_name == "Entry":
                        node = EntryItem.fromXml(xr, scene)
                    elif element_name == "Vertex":
                        node = VertexItem.fromXml(xr)
                        scene.addItem(node)
                        scene._graph.add_node(node)
                    if len(nodes) != node_id:
                        logger().warning(
                            "Entry ID mismatch: "
                            f"got {node_id}, expected {len(nodes)}"
                        )
                    nodes.append(node)
                elif element_name == "PhysicalNet":
                    edges_str = xr.attributes().value("Edges")
                    pairs_str = edges_str.split(" ")
                    for pair_str in pairs_str:
                        id1, id2 = pair_str.split(",")
                        vtx1, vtx2 = nodes[int(id1)], nodes[int(id2)]
                        cmd = CmdAddSegment(scene, vtx1, vtx2)
                        cmdExec(scene, cmd, undoable=False)
                elif item_name in _item_classes:
                    item_cls : "ItemXmlMixin" = _item_classes[item_name]
                    item = item_cls.fromXml(xr)
                    scene.addItem(item)
                else:
                    logger().warning(f"Unexpected element: {element_name}")
            xr.readNext()
        return scene
