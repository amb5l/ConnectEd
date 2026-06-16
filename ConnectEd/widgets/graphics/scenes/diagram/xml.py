from typing import Self

from PyQt6.QtCore    import QPointF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsItem

from .....app import logger

from .....core.check import checked
from .....core.defs  import APP_NAME

from ...xml import toXmlBegin, toXmlProperties, toXmlEnd, fromXmlProperties

from ...items.role    import DocumentItem
from ...items.symbol  import SymbolItem
from ...items.segment import SegmentItem, SegmentPreviewItem
from ...items.node    import NodeItem

from ...items.mixin   import ItemXmlMixin

from .netlist import _netNameAndSuffix

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DiagramScene


class DiagramSceneXmlMixin:
    @checked
    def toXml(self : "Self | DiagramScene", xw : QXmlStreamWriter) -> None:
        items = self.items()
        # scene root
        toXmlBegin(self.__class__.__name__.replace("Scene", ""), xw)
        # attributes
        toXmlProperties(self, xw)
        # symbol definitions
        self._toXmlSymbols(items, xw)
        # non-connectivity items
        self._toXmlNonConnectivityItems(items, xw)
        # node IDs
        id_by_node : dict[NodeItem, int] = {}
        for node, id in id_by_node.items():
            id_by_node[node] = id
            node.toXml(xw, id)
        # subnets and segments (specifying node IDs)
        for subnet in self.netlist.subnets():
            xw.writeStartElement("Subnet")
            xw.writeAttribute("ID", str(subnet.id))
            for segment in self.netlist.subnetSegments(subnet):
                id1 = id_by_node[segment.node1()]
                id2 = id_by_node[segment.node2()]
                segment.toXml(xw, (id1, id2))
            xw.writeEndElement()
        # nets
        for net in self.netlist.nets().values():
            xw.writeStartElement("Net")
            net_name = net.name + \
                f"[{net.suffix}]" if net.suffix is not None else ""
            xw.writeAttribute("Name", net_name)
            xw.writeAttribute(
                "Subnets",
                ",".join(str(subnet.id) for subnet in net.subnets)
            )
            xw.writeEndElement()
        # scene end
        toXmlEnd(xw)

    @checked
    def toXmlClipboard(
        self  : "Self | DiagramScene",
        items : list[QGraphicsItem],
        pos   : QPointF,
        xw    : QXmlStreamWriter,
    ) -> None:
        # clipboard root
        toXmlBegin("Clipboard", xw)
        # attributes
        xw.writeAttribute("X", str(pos.x()))
        xw.writeAttribute("Y", str(pos.y()))
        # symbols
        self._toXmlSymbols(items, xw)
        # non-connectivity items
        self._toXmlNonConnectivityItems(items, xw)
        # segments
        for item in items:
            if isinstance(item, SegmentItem):
                item.toXml(xw)
        # clipboard end
        toXmlEnd(xw)

    @classmethod
    @checked
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        scene = cls(fresh=False)
        scene.loadFromXml(xr)
        return scene

    @checked
    def loadFromXml(self : "Self | DiagramScene", xr : QXmlStreamReader) -> None:
        # lookups accessed by helpers
        node_by_id : dict[int, NodeItem] = {}
        id_by_node : dict[NodeItem, int] = {}
        subnet_xml_id_by_id : dict[int, int] = {}
        # subnet helper
        def fromXmlSubnet() -> None:
            # read attributes
            xml_subnet_id = int(xr.attributes().value("ID"))
            xml_subnet_node_ids = {
                int(part)
                for part in xr.attributes().value("Nodes").split(",")
                if part
            }
            xr.readNext()
            # load segments
            subnet_ids_before = set(self._subnets.keys())
            while not (xr.isEndElement() and xr.name() == "Subnet"):
                if xr.isStartElement():
                    child_name = xr.name()
                    if child_name == "Segment":
                        nodes_str = xr.attributes().value("Nodes")
                        node_id1, node_id2 = (
                            int(part) for part in nodes_str.split(",")
                        )
                        node1 = node_by_id.get(node_id1)
                        node2 = node_by_id.get(node_id2)
                        segment = SegmentItem(node1, node2)
                        self._scene.addItem(segment)
                        self.addSegment(segment)
                        node1.onConnectionChanged()
                        node2.onConnectionChanged()
                    else:
                        logger().warning(
                            f"Unexpected Subnet child: {child_name}"
                        )
                xr.readNext()
            subnet_ids_after = set(self._subnets.keys())
            # resolve newly created subnet
            added_subnet_ids = subnet_ids_after - subnet_ids_before
            if len(added_subnet_ids) == 1:
                subnet = self._subnets[added_subnet_ids.pop()]
                subnet_node_ids = {
                    id_by_node[node] for node in subnet.nodes
                }
                if subnet_node_ids != xml_subnet_node_ids:
                    logger().warning(
                        f"Subnet {xml_subnet_id} node mismatch: "
                        f"expected {sorted(xml_subnet_node_ids)}, "
                        f"got {sorted(subnet_node_ids)}"
                    )
                # record XML ID for later update
                subnet_xml_id_by_id[subnet.id] = xml_subnet_id
            elif len(added_subnet_ids) == 0:
                logger().warning(
                    "Segment load created no new subnet"
                )
            else:
                logger().warning(
                    f"Subnet {xml_subnet_id}: expected one new "
                    f"subnet, got {sorted(added_subnet_ids)}"
                )
            xr.readNext()
        # net helper
        def fromXmlNet() -> None:
            xml_net_name = xr.attributes().value("Name")
            xml_net_base_name, _ = \
                _netNameAndSuffix(xml_net_name)
            xml_subnet_ids = {
                int(part)
                for part in xr.attributes().value("Subnets").split(",")
                if part
            }
            if xml_net_base_name:
                net = self.nets().get(xml_net_base_name, None)
            elif len(xml_subnet_ids) == 1:
                xml_subnet_id = next(iter(xml_subnet_ids))
                internal_id = next(
                    (
                        sid for sid, xid in subnet_xml_id_by_id.items()
                        if xid == xml_subnet_id
                    ),
                    xml_subnet_id,
                )
                net = self.nets().get(internal_id, None)
            else:
                net = None
            if net is None:
                logger().warning(f"Net {xml_net_name!r} not found")
            else:
                expected_subnet_ids = {
                    next(
                        (
                            sid for sid, xid in subnet_xml_id_by_id.items()
                            if xid == xid_xml
                        ),
                        xid_xml,
                    )
                    for xid_xml in xml_subnet_ids
                }
                if net.subnets != expected_subnet_ids:
                    logger().warning(
                        f"Net {xml_net_name!r} subnet mismatch: "
                        f"expected {sorted(xml_subnet_ids)}, "
                        f"got {sorted(net.subnets)}"
                    )
            xr.readNext()
        # read start element
        top_element_name = self.__class__.__name__.replace("Scene", "")
        if xr.name() != top_element_name:
            raise ValueError(f"Expected {top_element_name} element, got {xr.name()}")
        # read attributes
        fromXmlProperties(self.properties, xr)
        # read items
        from ...items import _item_classes
        while not (xr.isEndElement() and xr.name() == top_element_name):
            if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                element_name = xr.name()
                item_name = element_name + "Item"
                if element_name == "Netlist":
                    while not (xr.isEndElement() and xr.name() == "Netlist"):
                        element_name = xr.name()
                        match element_name:
                            case "Subnet":
                                fromXmlSubnet()
                            case "Net":
                                fromXmlNet()
                            case _:
                                logger().warning(f"Unexpected element: {element_name}")
                                xr.readNext()
                    xr.readNext()
                elif item_name in _item_classes:
                    # read item
                    item_cls : "ItemXmlMixin" = _item_classes[item_name]
                    item = item_cls.fromXml(xr)
                    self.addItem(item)
                else:
                    logger().warning(f"Unexpected element: {element_name}")
                    xr.readNext()
            xr.readNext()
        self.properties.setNotify(True)  # enable property change signalling

    @checked
    def fromXmlClipboard(
        self  : "Self | DiagramScene",
        xr    : QXmlStreamReader
    ) -> tuple[QPointF, list[QGraphicsItem]]:
        items = []
        # read start element
        top_element_name = "Clipboard"
        if xr.name() != top_element_name:
            raise ValueError(f"Expected {top_element_name} element, got {xr.name()}")
        # read attributes
        xml_attrs = xr.attributes()
        for xml_attr in xml_attrs:
            if xml_attr.name() == "X":
                x = float(xml_attr.value())
            elif xml_attr.name() == "Y":
                y = float(xml_attr.value())
            else:
                logger().warning(f"Unexpected attribute: {xml_attr.name()}")
                xr.readNext()
        pos = QPointF(x, y)
        # read items
        from ...items import _item_classes
        while not (xr.isEndElement() and xr.name() == top_element_name):
            if xr.isStartElement():
                element_name = xr.name()
                item_name = element_name + "Item"
                if element_name == "Segment":
                    item = SegmentPreviewItem.fromXml(xr)
                    items.append(item)
                elif item_name in _item_classes:
                    item_cls : type[ItemXmlMixin] = _item_classes[item_name]
                    item = item_cls.fromXml(xr)
                    items.append(item)
                else:
                    logger().warning(f"Unexpected element: {element_name}")
                    xr.readNext()
        return pos, items

    @checked
    def _toXmlSymbols(
        self  : "Self | DiagramScene",
        items : list[QGraphicsItem],
        xw    : QXmlStreamWriter
    ) -> None:
        """Write symbol definitions."""
        if not items:
            return
        toXmlBegin("Symbols", xw)
        for item in items:
            if isinstance(item, SymbolItem):
                item.toXmlDefinition(xw)
        toXmlEnd(xw)

    @checked
    def _toXmlNonConnectivityItems(
        self  : "Self | DiagramScene",
        items : list[QGraphicsItem],
        xw    : QXmlStreamWriter
    ) -> None:
        # unparented DocumentItems except segments and nodes
        for item in items:
            if not isinstance(item, DocumentItem) \
            or not isinstance(item, ItemXmlMixin) \
            or item.parentItem() is not None \
            or isinstance(item, SegmentItem | NodeItem):
                continue
            item.toXml(xw)
