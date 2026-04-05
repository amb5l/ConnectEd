import uuid
import networkx

from typing import Self

from PyQt6.QtCore    import QPointF, QRectF, QSizeF, \
                            QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtGui     import QUndoStack, QColor

from .....app import logger, settings

from .....core.types import DataKind
from .....core.xml   import toXmlAttrs, fromXmlAttrs

from ...properties import InherentProperty, PropertiesMixin

from ...items.vertex import VertexItem, EntryItem

from ...items.mixin.xml import ItemXmlMixin

from .api       import DrawingSceneApiMixin
from .grips     import DrawingSceneGripsMixin
from .resources import DrawingSceneResourcesMixin
from .guides    import DrawingSceneGuidesMixin
from .private   import DrawingSceneApiPrivateMixin

from .cmd      import cmdExec
from .cmd.conn import CmdAddSegment


class DrawingScene(
    DrawingSceneApiMixin,
    DrawingSceneGripsMixin,
    DrawingSceneResourcesMixin,
    DrawingSceneGuidesMixin,
    DrawingSceneApiPrivateMixin,
    PropertiesMixin,
    QGraphicsScene
):
    # class attributes
    _PROPERTIES = {
        "Name" : InherentProperty(
            kind   = DataKind.STR,
            getter = lambda self: self._name,
            setter = lambda self, value : setattr(self, "_name", value)
        )
    }

    # instance attributes
    _uuid      : str
    _name      : str | None
    _sel_line  : QColor
    _sel_fill  : QColor
    _sel_text  : QColor
    _graph     : networkx.Graph
    undo_stack : QUndoStack | None

    def __init__(
        self    : Self,
        extents : QSizeF | None = None,
        fresh   : bool = True
    ) -> None:
        super().__init__()
        self._uuid = str(uuid.uuid4())
        self._name = None
        self._graph = networkx.Graph()
        self.updateSceneRect(extents)
        self.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)
        self.undo_stack = QUndoStack(self)
        self.initProperties(fresh)
        self.initResources()
        self.initGrips()
        self.onSettingsChange()
        settings().changed.connect(self.onSettingsChange)
        self.selectionChanged.connect(self.onSelectionChanged)

    def __hash__(self : Self):
        return hash(self._uuid)

    def __eq__(self : Self, other):
        if not isinstance(other, DrawingScene):
            return NotImplemented
        return self._uuid == other._uuid

    def onSettingsChange(self : Self) -> None:
        self._sel_line = settings().get("theme/selected/line")
        self._sel_fill = settings().get("theme/selected/fill")
        self._sel_text = settings().get("theme/selected/text")

    def onSelectionChanged(self : Self) -> None:
        self.updateGrips()

    def name(self : Self) -> str | None:
        return self._name

    def setName(self : Self, name : str | None) -> None:
        self._name = name

    def undo(self : Self) -> None:
        self.undo_stack.undo()

    def redo(self : Self) -> None:
        self.undo_stack.redo()

    def updateSceneRect(self : Self, rect : QRectF | None = None) -> None:
        ext_rect = QRectF(QPointF(0, 0), settings().get("defaults/extents"))
        scene_rect = QRectF(rect) if rect is not None else ext_rect
        for item in self.items():
            item_rect = item.mapToScene(item.boundingRect()).boundingRect()
            scene_rect = item_rect if scene_rect is None \
                else scene_rect.united(item_rect)
        if scene_rect is not None:
            # triple size of calculated scene rect
            w = scene_rect.size().width()
            h = scene_rect.size().height()
            scene_rect.setRect(
                scene_rect.left() - w,
                scene_rect.top() - h,
                w * 3,
                h * 3
            )
            self.setSceneRect(scene_rect)

    def selectedLineColor(self : Self) -> QColor:
        return self._sel_line

    def selectedFillColor(self : Self) -> QColor:
        return self._sel_fill

    def selectedTextColor(self : Self) -> QColor:
        return self._sel_text

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        # start
        xw.writeStartElement(self.__class__.__name__.replace("Scene", ""))
        # properties
        toXmlAttrs(self, xw)
        # items
        # must be top level (unparented); exclude vertices and segments
        for item in self.items():
            if item.parentItem() is None:
                if isinstance(item, ItemXmlMixin):
                    item.toXml(xw)
                else:
                    logger().warning(f"Unexpected item: {item.type()}")
        # entries, vertices and PropertyLabelItem instances
        raw_nodes : list[VertexItem] = list(self._graph.nodes())
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
        nodes : list["VertexItem | None"] = []
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
