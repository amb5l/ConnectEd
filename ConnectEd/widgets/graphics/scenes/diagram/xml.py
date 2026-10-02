from __future__ import annotations

from typing          import Self, cast

from PyQt6.QtCore    import QPointF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsItem

from .....app import logger

from .....core.check import checked
from .....core.utils import val2str
from .....core.xml   import toXmlStartElement, toXmlEndElement, \
                            fromXml, copyXml, pasteXml, XmlProtocol

from ...xml import toXmlProperties, fromXmlProperties, \
                   surveyXmlDefaults, writeXmlDefaults, \
                   readXmlDefaults, bindXmlDefaults, unbindXmlDefaults

from ...properties import PropertiesMixin

from ...items.role import DocumentItem

# decorative items
from ...items.line      import LineItem
from ...items.rectangle import RectangleItem
from ...items.ellipse   import EllipseItem
from ...items.polyline  import PolylineItem
from ...items.text      import TextItem

# functional items
from ...items.port     import PortItem
from ...items.gate     import GateItem, BufGateItem, AndGateItem, \
                              OrGateItem, XorGateItem
from ...items.block    import BlockItem
from ...items.symbol   import SymbolDefinitionItem, SymbolInstanceItem
from ...items.port_pin import PortPinMixin

# connectivity items
from ...items.segment   import SegmentItem
from ...items.node      import NodeItem, FreeNodeItem, FixedNodeItem
from ...items.net_label import NetLabelItem

from ...items.mixin.xml import ItemXmlMixin

from .netlist import _netNameAndSuffix
from .host    import asDiagramScene


def _iter_xml_tree(item : QGraphicsItem, pins : bool) -> list[QGraphicsItem]:
    found = [item]
    if pins:
        for child in item.childItems():
            if isinstance(child, PortPinMixin):
                found.extend(_iter_xml_tree(child, True))
    if isinstance(item, PropertiesMixin):
        seen : set[int] = set()
        for prop in item.properties.values():
            for text in item.propertyTextItems(prop):
                if id(text) in seen:
                    continue
                seen.add(id(text))
                found.extend(_iter_xml_tree(text, False))
    return found


class DiagramSceneXmlMixin:
    _XML_TAG = "HdlSchematicDiagram"

    # -- save --------------------------------------------------------------

    @checked
    def toXml(
        self  : Self,
        xw    : QXmlStreamWriter,
        items : QGraphicsItem | list[QGraphicsItem] | None = None,
    ) -> None:
        host = asDiagramScene(self)
        full_scene = items is None
        if full_scene:
            items = host.items()
        elif not isinstance(items, list):
            items = [items]
        # filter out unparented items
        items = [item for item in items if item.parentItem() is None]
        if not items:
            return
        # output
        token    = None
        defaults : dict[str, dict[str, str]] = {}
        if full_scene:
            defaults = surveyXmlDefaults(host._xmlDefaultsItems(items))
            token = bindXmlDefaults(defaults)
        try:
            if full_scene:
                # start scene element
                toXmlStartElement(xw, host._XML_TAG)
                toXmlProperties(host, xw)
                writeXmlDefaults(xw, defaults)
            # symbol definitions
            host._toXmlSymbolDefinitions(xw, items)
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
            host._toXmlNetlist(xw)
            if full_scene:
                # end scene element
                toXmlEndElement(xw)
        finally:
            if token is not None:
                unbindXmlDefaults(token)

    def _xmlDefaultsItems(
        self  : Self,
        items : list[QGraphicsItem],
    ) -> list[PropertiesMixin]:
        host = asDiagramScene(self)
        found : list[PropertiesMixin] = []

        def add(item : QGraphicsItem, pins : bool) -> None:
            for obj in _iter_xml_tree(item, pins):
                if isinstance(obj, PropertiesMixin) \
                and callable(getattr(type(obj), "xmlTag", None)):
                    found.append(obj)

        symbols = host.getSymbols().values()
        instances = [
            item for item in items if isinstance(item, SymbolInstanceItem)
        ]
        if instances:
            symbol_names = {symbol.name() for symbol in symbols}
            used_names = {instance.name() for instance in instances}
            for symbol in symbols:
                if symbol.name() in symbol_names & used_names:
                    add(symbol, True)
        for item in items:
            if not isinstance(item, DocumentItem) \
            or not isinstance(item, ItemXmlMixin) \
            or item.parentItem() is not None \
            or isinstance(item, SegmentItem | NodeItem):
                continue
            pins = not isinstance(item, GateItem | SymbolInstanceItem)
            add(item, pins)
        return found

    @checked
    def copy(
        self  : Self,
        items : QGraphicsItem | list[QGraphicsItem],
        pos   : QPointF       | None = None
    ) -> None:
        host = asDiagramScene(self)
        items = host._topItems(items)
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
        host = asDiagramScene(self)
        symbols = host.getSymbols().values()
        instances = [
            item for item in items if isinstance(item, SymbolInstanceItem)
        ]
        if not instances:
            return
        symbol_names = {symbol.name() for symbol in symbols}
        used_names = {instance.name() for instance in instances}
        undefined_names = used_names - symbol_names
        if undefined_names:
            logger().warning(f"Undefined symbols: {undefined_names}")
        used_defined_names = symbol_names & used_names
        if not used_defined_names:
            return
        toXmlStartElement(xw, "Symbols")
        for symbol in symbols:
            if symbol.name() not in used_defined_names:
                continue
            symbol.toXml(xw)
        toXmlEndElement(xw)

    @checked
    def _toXmlNetlist(self : Self, xw : QXmlStreamWriter) -> None:
        host = asDiagramScene(self)
        toXmlStartElement(xw, "Netlist")
        id_by_node = {
            node: node_id for node_id, node in enumerate(host.netlist.nodes())
        }
        for node in sorted(id_by_node, key=lambda n : id_by_node[n]):
            if isinstance(node, FixedNodeItem):
                node.toXml(xw, id_by_node[node])
            elif isinstance(node, FreeNodeItem) \
            and node.parentItem() is None:
                node.toXml(xw, id_by_node[node])
        for subnet in sorted(
            host.netlist.subnets().values(),
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
        for net in host.netlist.nets().values():
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
        scene = DiagramScene(doc=None, fresh=False)
        scene.loadFromXml(xr)
        return cast(Self, scene)

    @checked
    def loadFromXml(
        self : Self,
        xr   : QXmlStreamReader
    ) -> None:
        host = asDiagramScene(self)
        node_by_id          : dict[int, NodeItem] = {}
        id_by_node          : dict[NodeItem, int] = {}
        subnet_xml_id_by_id : dict[int, int] = {}

        def fromXmlFixedNode(xr : QXmlStreamReader) -> None:
            node_id, pos = NodeItem.fromXml(xr)
            node : FixedNodeItem | None = None
            for item in host.items(pos):
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
            for item in host.items(pos):
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
            for subnet in host.netlist.subnets().values():
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
                net = host.netlist.nets().get(xml_net_base_name, None)
            elif len(xml_subnet_ids) == 1:
                xml_subnet_id = next(iter(xml_subnet_ids))
                internal_id = next(
                    (
                        sid for sid, xid in subnet_xml_id_by_id.items()
                        if xid == xml_subnet_id
                    ),
                    xml_subnet_id,
                )
                net = host.netlist.nets().get(internal_id, None)
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

        def fromXmlDefinitions(xr : QXmlStreamReader) -> None:
            xr.readNext()
            symbols = fromXml(xr, {
                "Symbol" : SymbolDefinitionItem
            }, ptag="Symbols")
            host.addSymbols(symbols)

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
                    host.addSegment(p1, p2, undoable=False)
                else:
                    logger().warning("Segment missing X1/Y1/X2/Y2 attributes")
            else:
                if not isinstance(item := item_cls.fromXml(xr), QGraphicsItem):
                    raise TypeError("Bad item")
                host.addItem(item)
                if isinstance(item, SymbolInstanceItem):
                    name = item.name()
                    definition = host.getSymbol(name)
                    if definition:
                        item.syncFromDefinition(definition)
                    else:
                        logger().warning(f"Symbol {name} not found")

        top_element_name = host._XML_TAG
        if xr.name() != top_element_name:
            raise ValueError(
                f"Expected {top_element_name} element, got {xr.name()}"
            )
        fromXmlProperties(host, xr)

        defaults_token = None

        def fromXmlDefaults(xr : QXmlStreamReader) -> None:
            nonlocal defaults_token
            defaults_token = bindXmlDefaults(readXmlDefaults(xr))

        xref = {
            "Defaults" : fromXmlDefaults,
            "Symbols"  : fromXmlDefinitions,
            "Netlist"  : fromXmlNetlist
        }
        for item_name, item_cls in diagram_scene_xml_items.items():
            xref[item_name] = \
                lambda xr, cls=item_cls: (fromXmlItem(xr, cls), None)[1]

        try:
            fromXml(xr, xref, ptag=top_element_name)
            host.setPropertiesLive(True)
        finally:
            if defaults_token is not None:
                unbindXmlDefaults(defaults_token)

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
