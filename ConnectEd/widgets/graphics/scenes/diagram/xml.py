from __future__ import annotations

from typing          import Self, cast

from PyQt6.QtCore    import QPointF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsItem

from .....app import logger

from .....core.check import checked
from .....core.utils import val2str
from .....core.xml   import toXmlStartElement, toXmlEndElement, \
                            fromXml, copyXml, pasteXml, XmlProtocol

from ...xml import toXmlProperties, fromXmlProperties

from ...items.role    import DocumentItem

# decorative items
from ...items.line      import LineItem
from ...items.rectangle import RectangleItem
from ...items.ellipse   import EllipseItem
from ...items.polyline  import PolylineItem
from ...items.text      import TextItem

# functional items
from ...items.port      import PortItem
from ...items.gate      import BufGateItem, AndGateItem, OrGateItem, XorGateItem
from ...items.block     import BlockItem
from ...items.symbol    import SymbolDefinitionItem, SymbolInstanceItem

# connectivity items
from ...items.segment   import SegmentItem
from ...items.node      import NodeItem, FreeNodeItem, FixedNodeItem
from ...items.net_label import NetLabelItem

from ...items.mixin.xml import ItemXmlMixin

from .netlist import _netNameAndSuffix

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DiagramScene


class DiagramSceneXmlMixin:
    _XML_TAG = "HdlSchematicDiagram"

    # -- save --------------------------------------------------------------

    @checked
    def toXml(
        self  : Self,
        xw    : QXmlStreamWriter,
        items : QGraphicsItem | list[QGraphicsItem] | None = None,
    ) -> None:
        from . import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        full_scene = items is None
        if full_scene:
            items = self.items()
        elif not isinstance(items, list):
            items = [items]
        # filter out unparented items
        items = [item for item in items if item.parentItem() is None]
        if not items:
            return
        # output
        if full_scene:
            # start scene element
            toXmlStartElement(xw, self._XML_TAG)
            toXmlProperties(self, xw)
        # symbol definitions
        self._toXmlSymbolDefinitions(xw, items)
        # non-connectivity items
        for item in items:
            if not isinstance(item, DocumentItem) \
            or not isinstance(item, ItemXmlMixin) \
            or item.parentItem() is not None \
            or isinstance(item, SegmentItem | NodeItem):
                continue
            item.toXml(xw)
        # segments
        for item in items:
            if isinstance(item, SegmentItem):
                item.toXml(xw)
        self._toXmlNetlist(xw)
        if full_scene:
            # end scene element
            toXmlEndElement(xw)

    @checked
    def copy(
        self  : Self,
        items : QGraphicsItem | list[QGraphicsItem],
        pos   : QPointF | None = None
    ) -> None:
        from . import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        items = self._topItems(items)
        metadata = None
        if pos is not None:
            metadata = {"X" : val2str(pos.x()), "Y" : val2str(pos.y())}
        copyXml(cast(list[XmlProtocol], items), metadata)

    @checked
    def _toXmlSymbolDefinitions(
        self  : Self,
        xw    : QXmlStreamWriter,
        items : list[QGraphicsItem]
    ) -> None:
        """Serialise symbols that are used in the scene."""
        from . import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        definitions = self.symbolDefinitions()
        instances = [
            item for item in items if isinstance(item, SymbolInstanceItem)
        ]
        if not instances:
            return
        definition_names = \
            {definition.name() for definition in definitions.values()}
        used_names = {instance.name() for instance in instances}
        undefined_names = used_names - definition_names
        if undefined_names:
            logger().warning(f"Undefined symbols: {undefined_names}")
        used_defined_names = definition_names & used_names
        if not used_defined_names:
            return
        toXmlStartElement(xw, "Symbols")
        for name, symbol in definitions.items():
            if name not in used_defined_names:
                continue
            symbol.toXml(xw)
        toXmlEndElement(xw)

    @checked
    def _toXmlNetlist(self : Self, xw : QXmlStreamWriter) -> None:
        from . import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        toXmlStartElement(xw, "Netlist")
        id_by_node = {
            node: node_id for node_id, node in enumerate(self.netlist.nodes())
        }
        for node in sorted(id_by_node, key=lambda n : id_by_node[n]):
            if isinstance(node, FixedNodeItem):
                node.toXml(xw, id_by_node[node])
            elif isinstance(node, FreeNodeItem) \
            and node.parentItem() is None:
                node.toXml(xw, id_by_node[node])
        for subnet in sorted(
            self.netlist.subnets().values(),
            key=lambda s : -1 if s.id is None else s.id,
        ):
            xw.writeStartElement("Subnet")
            xw.writeAttribute("ID", str(subnet.id))
            xw.writeAttribute(
                "Nodes",
                ",".join(
                    str(id_by_node[node])
                    for node in sorted(
                        subnet.nodes,
                        key=lambda n : id_by_node[n],
                    )
                ),
            )
            xw.writeEndElement()
        for net in self.netlist.nets().values():
            if net.name is None:
                continue
            xw.writeStartElement("Net")
            net_name = net.name
            if net.suffix is not None and net.suffix != "":
                net_name += f"[{net.suffix}]"
            xw.writeAttribute("Name", net_name)
            xw.writeAttribute(
                "Subnets",
                ",".join(str(sid) for sid in sorted(net.subnets)),
            )
            xw.writeEndElement()
        toXmlEndElement(xw)

    # -- load --------------------------------------------------------------

    @classmethod
    @checked
    def fromXml(cls : type[Self], xr : QXmlStreamReader) -> Self:
        from . import DiagramScene
        if not issubclass(cls, DiagramScene):
            raise TypeError("Bad host")
        scene = cls(doc=None, fresh=False)
        scene.loadFromXml(xr)
        return scene

    @checked
    def loadFromXml(
        self : Self,
        xr   : QXmlStreamReader
    ) -> None:
        from . import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        node_by_id : dict[int, NodeItem] = {}
        id_by_node : dict[NodeItem, int] = {}
        subnet_xml_id_by_id : dict[int, int] = {}

        def fromXmlFixedNode(xr : QXmlStreamReader) -> None:
            node_id, pos = NodeItem.fromXml(xr)
            node : FixedNodeItem | None = None
            for item in self.items(pos):
                if isinstance(item, FixedNodeItem):
                    node = item
                    break
            if node is None:
                logger().warning(
                    f"FixedNode {node_id} not found at "
                    f"({pos.x()}, {pos.y()})"
                )
            else:
                node_by_id[node_id] = node
                id_by_node[node] = node_id

        def fromXmlFreeNode(xr : QXmlStreamReader) -> None:
            node_id, pos = NodeItem.fromXml(xr)
            node : FreeNodeItem | None = None
            for item in self.items(pos):
                if isinstance(item, FreeNodeItem) \
                and item.parentItem() is None:
                    node = item
                    break
            if node is None:
                logger().warning(
                    f"FreeNode {node_id} not found at "
                    f"({pos.x()}, {pos.y()})"
                )
            else:
                node_by_id[node_id] = node
                id_by_node[node] = node_id

        def fromXmlSubnet(xr : QXmlStreamReader) -> None:
            xml_subnet_id = int(xr.attributes().value("ID"))
            xml_subnet_node_ids = {
                int(part)
                for part in xr.attributes().value("Nodes").split(",")
                if part
            }
            matched : int | None = None
            for subnet in self.netlist.subnets().values():
                node_ids = {
                    id_by_node[node]
                    for node in subnet.nodes
                    if node in id_by_node
                }
                if len(node_ids) != len(subnet.nodes):
                    continue
                if node_ids == xml_subnet_node_ids:
                    matched = subnet.id
                    break
            if matched is None:
                logger().warning(
                    f"Subnet {xml_subnet_id} not found for "
                    f"nodes {sorted(xml_subnet_node_ids)}"
                )
            else:
                subnet_xml_id_by_id[matched] = xml_subnet_id

        def fromXmlNet(xr : QXmlStreamReader) -> None:
            xml_net_name = xr.attributes().value("Name")
            xml_net_base_name, _ = \
                _netNameAndSuffix(xml_net_name)
            xml_subnet_ids = {
                int(part)
                for part in xr.attributes().value("Subnets").split(",")
                if part
            }
            if xml_net_base_name:
                net = self.netlist.nets().get(xml_net_base_name, None)
            elif len(xml_subnet_ids) == 1:
                xml_subnet_id = next(iter(xml_subnet_ids))
                internal_id = next(
                    (
                        sid for sid, xid in subnet_xml_id_by_id.items()
                        if xid == xml_subnet_id
                    ),
                    xml_subnet_id,
                )
                net = self.netlist.nets().get(internal_id, None)
            else:
                net = None
            if net is None:
                logger().warning(f"Net {xml_net_name!r} not found")
            else:
                expected_subnet_ids = {
                    sid for sid, xid in subnet_xml_id_by_id.items()
                    if xid in xml_subnet_ids
                }
                if net.subnets != expected_subnet_ids:
                    got_subnet_ids = sorted(
                        subnet_xml_id_by_id.get(s, s) for s in net.subnets
                    )
                    logger().warning(
                        f"Net {xml_net_name!r} subnet mismatch: "
                        f"expected {sorted(xml_subnet_ids)}, "
                        f"got {got_subnet_ids}"
                    )

        def fromXmlNetlist(xr : QXmlStreamReader) -> None:
            xr.readNext()
            fromXml(xr, {
                "FixedNode" : fromXmlFixedNode,
                "FreeNode"  : fromXmlFreeNode,
                "Subnet"    : fromXmlSubnet,
                "Net"       : fromXmlNet,
            }, ptag="Netlist")

        def fromXmlSymbolDefinitions(xr : QXmlStreamReader) -> None:
            xr.readNext()
            symbols = fromXml(
                xr,
                { "Symbol" : SymbolDefinitionItem },
                ptag="Symbols"
            )
            self._symbols |= {symbol.name(): symbol for symbol in symbols}

        def fromXmlItem(
            xr       : QXmlStreamReader,
            item_cls : type[XmlProtocol]
        ) -> None:
            if item_cls == SegmentItem:
                attrs = xr.attributes()
                x1 = attrs.value("X1")
                if x1:
                    p1 = QPointF(float(x1), float(attrs.value("Y1")))
                    p2 = QPointF(float(attrs.value("X2")), float(attrs.value("Y2")))
                    self.addSegment(p1, p2, undoable=False)
                else:
                    logger().warning("Segment missing X1/Y1/X2/Y2 attributes")
            else:
                if not isinstance(item := item_cls.fromXml(xr), QGraphicsItem):
                    raise TypeError("Bad item")
                self.addItem(item)
                if isinstance(item, SymbolInstanceItem):
                    name = item.name()
                    definition = self._symbols.get(name, None)
                    if definition:
                        item.syncFromDefinition(definition)
                    else:
                        logger().warning(f"Symbol {name} not found")

        top_element_name = self._XML_TAG
        if xr.name() != top_element_name:
            raise ValueError(
                f"Expected {top_element_name} element, got {xr.name()}"
            )
        fromXmlProperties(self, xr)

        xref = {
            "Symbols" : fromXmlSymbolDefinitions,
            "Netlist" : fromXmlNetlist
        }
        for item_name, item_cls in diagram_scene_xml_items.items():
            xref[item_name] = \
                lambda xr, cls=item_cls: (fromXmlItem(xr, cls), None)[1]

        fromXml(xr, xref, ptag=top_element_name)
        self.setLive(True)

    @checked
    def paste(self : Self) -> tuple[list[QGraphicsItem], QPointF | None]:
        items, attributes = pasteXml(diagram_scene_xml_items)
        x = attributes.get("X", None)
        y = attributes.get("Y", None)
        pos = None if x is None or y is None else QPointF(float(x), float(y))
        return cast(list[QGraphicsItem], items), pos

diagram_scene_xml_items : dict[str, type[XmlProtocol]] = {
    "Line"         : LineItem,
    "Rectangle"    : RectangleItem,
    "Ellipse"      : EllipseItem,
    "Polyline"     : PolylineItem,
    "Text"         : TextItem,
    "Port"         : PortItem,
    "BufGate"      : BufGateItem,
    "AndGate"      : AndGateItem,
    "OrGate"       : OrGateItem,
    "XorGate"      : XorGateItem,
    "Block"        : BlockItem,
    "Symbol"       : SymbolInstanceItem,
    "NetLabel"     : NetLabelItem,
    "Segment"      : SegmentItem
}
