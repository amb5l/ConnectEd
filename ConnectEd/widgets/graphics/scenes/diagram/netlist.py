import networkx

from typing      import Self
from dataclasses import dataclass, field

from PyQt6.QtCore import QXmlStreamReader, QXmlStreamWriter

from .....app import logger

from .....core.types import Direction
from .....core.expr  import evaluate
from .....core.check import checked

from ...items.node       import NodeItem, FreeNodeItem, FixedNodeItem, \
                                TapMajorNodeItem, TapMinorNodeItem
from ...items.net_label  import NetLabelItem
from ...items.tap        import TapItem
from ...items.port       import PortItem
from ...items.block_pin  import BlockPinItem
from ...items.symbol_pin import SymbolPinItem
from ...items.block      import BlockItem
from ...items.symbol     import SymbolItem
from ...items.segment  import SegmentItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...scenes.diagram import DiagramScene


@dataclass(slots=True)
class Subnet:
    """Corresponds to a connected component of the graph."""
    id     : int | None    = None  # None = uninitialised
    name   : str | None    = None  # None = unresolved
    suffix : str | None    = None  # None = unresolved
    nodes  : set[NodeItem] = field(default_factory=set)
    net    : "Net | None"  = None  # back-reference to parent net


@dataclass(slots=True)
class Net:
    """
    Either a single unresolved (unnamed) subnet,
    or one or more subnets with the same name.
    """
    name    : str | None = None  # base name (e.g. "data"); None when unresolved
    suffix  : str | None = None  # aggregate suffix across subnets
    subnets : set[int]   = field(default_factory=set)  # subnet IDs


class Netlist:
    # _nets keying:
    #   - resolved net  -> str key (the base name, e.g. _nets["data"])
    #   - unresolved    -> int key (the sole subnet's id, e.g. _nets[42])

    _scene       : "DiagramScene"
    _graph       : networkx.Graph
    _subnets     : dict[int, Subnet]
    _node2subnet : dict[NodeItem, int]
    _subnet_id   : int
    _nets        : dict[str | int, Net]
    _subnet2net  : dict[int, str | int]

    @checked
    def __init__(self : Self, scene : "DiagramScene") -> None:
        self._scene       = scene
        self._graph       = networkx.Graph()
        self._subnets     = {}
        self._node2subnet = {}
        self._subnet_id   = 0
        self._nets        = {}
        self._subnet2net  = {}

    # -- node methods ------------------------------------------------------

    @checked
    def nodes(self : Self) -> list[NodeItem]:
        return list(self._node2subnet.keys())

    @checked
    def hasNode(self : Self, node : NodeItem) -> bool:
        return node in self._graph

    @checked
    def nodeDegree(self : Self, node : NodeItem) -> int:
        """Number of segments connected to the node."""
        return self._graph.degree(node)

    @checked
    def nodeSegments(self : Self, node : NodeItem) -> list["SegmentItem"]:
        """Edges connected to the node."""
        iterator = self._graph.edges(node, data=True)
        return [data["segment"] for _, _, data in iterator]

    @checked
    def nodeSubnet(self : Self, node : NodeItem) -> Subnet | None:
        subnet_id = self._node2subnet.get(node, None)
        return None if subnet_id is None else self._subnets[subnet_id]

    @checked
    def nodeNet(self : Self, node : NodeItem) -> Net | None:
        subnet = self.nodeSubnet(node)
        return None if subnet is None else subnet.net

    @checked
    def nodeNameSuffixType(self : Self, node : NodeItem) -> tuple[str, str, str]:
        full_name = None
        if isinstance(node, FreeNodeItem):
            for child in node.childItems():
                if isinstance(child, NetLabelItem):
                    if child.name() == "Name":
                        full_name = child.value()
                        break
        elif isinstance(node, FixedNodeItem):
            node_parent = node.parentItem()
            if isinstance(node_parent, PortItem):
                full_name = node_parent.name()
            elif isinstance(node_parent, BlockPinItem | SymbolPinItem):
                pin_parent : BlockItem | SymbolItem | None = node_parent.parentItem()
                label = pin_parent.label()
                pin_name = node_parent.name()
                full_name = f"{label}_{pin_name}"
        if full_name is None:
            return "", "", "?"
        base_name, suffix = _baseNameAndSuffix(full_name)
        return base_name, suffix, "?"

    @checked
    def adoptNode(self : Self, node : NodeItem) -> None:
        """
        Repair subnet membership for a node already in the graph.
        Unwired scene-only nodes are not adopted until addSegment.
        """
        if node not in self._graph:
            return
        subnet_ids = self._subnetsContainingNode(node)
        if node in self._node2subnet:
            # node is already mapped to a subnet
            subnet_id = self._node2subnet[node]
            if subnet_ids != [subnet_id]:
                # mapping does not match subnet(s)
                subnet = self._subnets[subnet_id]
                if len(subnet_ids) == 0:
                    logger().warning(f"Node {node} mapped to subnet {subnet_id} which does not contain it.")
                    self._addNodesToSubnet(subnet, node)
                elif len(subnet_ids) == 1:
                    logger().warning(f"Node {node} mapped to subnet {subnet_id} but contained by subnet {subnet_ids[0]}.")
                    self._node2subnet[node] = subnet_ids[0]
                elif subnet_id in subnet_ids:
                    other_subnet_ids = subnet_ids.copy()
                    other_subnet_ids.remove(subnet_id)
                    logger().warning(f"Node {node} mapped to subnet {subnet_id} but also exists in subnets {other_subnet_ids}.")
                    for other_subnet_id in other_subnet_ids:
                        other_subnet = self._subnets[other_subnet_id]
                        self._removeNodeFromSubnet(node, other_subnet)
                else:
                    logger().warning(f"Node {node} mapped to subnet {subnet_id} but exists in subnets {subnet_ids}.")
                    # map to first subnet
                    self._node2subnet[node] = subnet_ids[0]
                    # remove from other subnets
                    for other_subnet_id in subnet_ids[1:]:
                        other_subnet = self._subnets[other_subnet_id]
                        self._removeNodeFromSubnet(node, other_subnet)
        else:
            # node is not mapped to any subnet
            if len(subnet_ids) == 0:
                logger().warning(
                    f"Node {node} is in the graph but has no subnet mapping."
                )
            elif len(subnet_ids) == 1:
                logger().warning(f"Node {node} has no subnet mapping but exists in subnet {subnet_ids[0]}.")
                self._node2subnet[node] = subnet_ids[0]
            else:
                logger().warning(f"Node {node} has no subnet mapping but exists in {len(subnet_ids)} subnets.")
                # map to first subnet
                self._node2subnet[node] = subnet_ids[0]
                # remove from other subnets
                for other_subnet_id in subnet_ids[1:]:
                    other_subnet = self._subnets[other_subnet_id]
                    self._removeNodeFromSubnet(node, other_subnet)

    @checked
    def removeNodes(self : Self, nodes : NodeItem | list[NodeItem]) -> None:
        if isinstance(nodes, NodeItem):
            nodes = [nodes]
        affected_subnets : set[Subnet] = set()
        for node in nodes:
            if node not in self._graph:
                continue
            self._graph.remove_node(node)
            subnet = self.nodeSubnet(node)
            if subnet is not None:
                self._node2subnet.pop(node, None)
                subnet.nodes.discard(node)
                if not subnet.nodes:
                    self._removeSubnet(subnet)
                else:
                    affected_subnets.add(subnet)
        self._resolveSubnets(affected_subnets)

    @checked
    def replaceNode(self : Self, node1 : NodeItem, node2 : NodeItem) -> None:
        if node1 not in self._graph:
            logger().error(f"Node {node1} is not in the graph.")
            return
        if node2 in self._graph:
            logger().error(f"Node {node2} is already in the graph.")
            return
        if node1 == node2:
            logger().warning("Specified nodes are the same.")
            return
        networkx.relabel_nodes(self._graph, {node1: node2})
        self._node2subnet[node2] = self._node2subnet[node1]
        self._node2subnet.pop(node1, None)
        self._resolveSubnet(self._subnets[self._node2subnet[node2]])

    # -- segment methods ---------------------------------------------------

    @checked
    def hasSegment(self : Self, node1 : NodeItem, node2 : NodeItem) -> bool:
        return self._graph.has_edge(node1, node2)

    @checked
    def addSegment(self : Self, seg : "SegmentItem") -> None:
        node1 = seg.node1()
        node2 = seg.node2()
        assert node1 is not None and node2 is not None
        for node in (node1, node2):
            if node not in self._graph:
                self._graph.add_node(node)
        self._graph.add_edge(node1, node2, segment=seg)
        subnet1 = self.nodeSubnet(node1)
        subnet2 = self.nodeSubnet(node2)
        if subnet1 is None and subnet2 is None:
            self._resolveSubnet(self._newSubnet({node1, node2}))
        elif subnet1 is None:
            self._addNodesToSubnet(subnet2, node1)
            self._resolveSubnet(subnet2)
        elif subnet2 is None:
            self._addNodesToSubnet(subnet1, node2)
            self._resolveSubnet(subnet1)
        elif subnet1 is subnet2:
            return
        else:
            subnet1.nodes |= subnet2.nodes
            for node in subnet2.nodes:
                self._node2subnet[node] = subnet1.id
            self._detachSubnetFromNet(subnet2)
            self._subnets.pop(subnet2.id, None)
            self._resolveSubnet(subnet1)

    @checked
    def removeSegment(self : Self, node1 : NodeItem, node2 : NodeItem) -> None:
        if not self._graph.has_edge(node1, node2):
            return
        self._graph.remove_edge(node1, node2)
        subnet1 = self.nodeSubnet(node1)
        if subnet1 is not None \
        and not networkx.has_path(self._graph, node1, node2):
            nodes1 = networkx.node_connected_component(self._graph, node1)
            nodes2 = networkx.node_connected_component(self._graph, node2)
            if len(nodes1) < len(nodes2):
                nodes1, nodes2 = nodes2, nodes1
            subnet1.nodes = nodes1
            subnet2 = self._newSubnet(nodes2)
            self._resolveSubnet(subnet1)
            self._resolveSubnet(subnet2)
        self._dropIsolated(node1)
        self._dropIsolated(node2)

    @checked
    def _dropIsolated(self : Self, node : NodeItem) -> None:
        """Remove a degree-0 node from the graph and subnet layer."""
        if node not in self._graph or self._graph.degree(node) != 0:
            return
        affected_subnets : set[Subnet] = set()
        subnet = self.nodeSubnet(node)
        if subnet is not None:
            self._node2subnet.pop(node, None)
            subnet.nodes.discard(node)
            if not subnet.nodes:
                self._removeSubnet(subnet)
            else:
                affected_subnets.add(subnet)
        self._graph.remove_node(node)
        self._resolveSubnets(affected_subnets)

    # -- subnet methods ----------------------------------------------------

    @checked
    def subnets(self : Self) -> dict[int, Subnet]:
        return self._subnets

    # -- net methods -------------------------------------------------------

    @checked
    def nets(self : Self) -> dict[str | int, Net]:
        return self._nets

    # -- serialisation/deserialisation -------------------------------------

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        items = self._scene.items()
        # start
        xw.writeStartElement("Connectivity")
        # 1. nodes
        scene_nodes = [item for item in items if isinstance(item, NodeItem)]
        graph_nodes = self.nodes()
        id_by_node : dict[NodeItem, int] = {}
        for id, node in enumerate(graph_nodes):
            id_by_node[node] = id
            node.toXml(xw, id)
            scene_nodes.remove(node)
        if scene_nodes:
            logger().warning(f"{len(scene_nodes)} nodes remaining after node processing.")
        # 2. subnets and segments
        scene_segments = \
            [item for item in items if isinstance(item, SegmentItem)]
        for subnet in self.subnets().values():
            subnet_node_ids = [id_by_node[node] for node in subnet.nodes]
            xw.writeStartElement("Subnet")
            xw.writeAttribute("ID", str(subnet.id))
            xw.writeAttribute(
                "Nodes",
                ",".join(str(node_id) for node_id in subnet_node_ids)
            )
            for segment in self._orderedSubnetSegments(subnet):
                node_id1 = id_by_node[segment.node1()]
                node_id2 = id_by_node[segment.node2()]
                xw.writeStartElement("Segment")
                xw.writeAttribute("Nodes", f"{node_id1},{node_id2}")
                xw.writeEndElement()
                scene_segments.remove(segment)
            xw.writeEndElement()
        if scene_segments:
            logger().warning(f"{len(scene_segments)} segments remaining after subnet processing.")
        # 3. nets
        for net in self.nets().values():
            net_base_name = net.name or ""
            net_suffix = net.suffix or ""
            net_name = net_base_name + net_suffix
            net_subnets = [self._subnets[subnet_id] for subnet_id in net.subnets]
            net_subnet_ids = [subnet.id for subnet in net_subnets]
            xw.writeStartElement("Net")
            xw.writeAttribute("Name", net_name)
            xw.writeAttribute(
                "Subnets",
                ",".join(str(subnet_id) for subnet_id in net_subnet_ids)
            )
            xw.writeEndElement()
        # end
        xw.writeEndElement()

    @checked
    def fromXml(self : Self, xr : QXmlStreamReader) -> None:
        if xr.name() != "Connectivity":
            raise ValueError(f"Expected Connectivity element, got {xr.name()}")
        node_by_id : dict[int, NodeItem] = {}
        id_by_node : dict[NodeItem, int] = {}
        subnet_xml_id_by_id : dict[int, int] = {}
        xr.readNext()
        while not (xr.isEndElement() and xr.name() == "Connectivity"):
            if xr.isStartElement():
                element_name = xr.name()
                match element_name:
                    case "FreeNode":
                        # create free node
                        id, pos = FreeNodeItem.fromXml(xr)
                        node = self._scene.addFreeNode(pos, undoable=False)
                        node_by_id[id] = node
                        id_by_node[node] = id
                    case name if name.endswith("Node") and name != "FreeNode":
                        # validate fixed node
                        id, pos = FixedNodeItem.fromXml(xr)
                        for item in self._scene.items(pos):
                            item_name = \
                                item.__class__.__name__.removesuffix("Item")
                            if name == item_name:
                                node_by_id[id] = item
                                id_by_node[item] = id
                                break
                        else:
                            logger().warning(f"No {name} found at {pos.x()}, {pos.y()}")
                    case "Subnet":
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
                                    self._segmentFromXml(xr, node_by_id)
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
                    case "Net":
                        xml_net_name = xr.attributes().value("Name")
                        xml_net_base_name, _ = \
                            _baseNameAndSuffix(xml_net_name)
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
                    case _:
                        logger().warning(
                            f"Unexpected Connectivity element: {element_name}"
                        )
            xr.readNext()

    # -- node helpers ------------------------------------------------------

    @checked
    def _subnetsContainingNode(self : Self, node : NodeItem) -> list[int]:
        """Returns list of subnets that contain the node."""
        subnet_ids = []
        for subnet in self._subnets.values():
            if node in subnet.nodes:
                subnet_ids.append(subnet.id)
        return subnet_ids

    # -- subnet helpers ----------------------------------------------------

    @checked
    def _newSubnet(
        self  : Self,
        nodes : NodeItem | set[NodeItem] | None = None
    ) -> Subnet:
        """Create new subnet, attached to a fresh unresolved net."""
        if isinstance(nodes, NodeItem):
            nodes = {nodes}
        subnet = Subnet(id=self._subnet_id)
        self._subnet_id += 1
        self._subnets[subnet.id] = subnet
        if nodes:
            self._addNodesToSubnet(subnet, nodes)
        # Every subnet must always belong to exactly one net. Start it off in
        # its own unresolved net, keyed by subnet id; later resolution may
        # migrate it into a named net.
        net = Net(name=None, suffix=None)
        self._nets[subnet.id] = net
        self._attachSubnetToNet(subnet, net)
        return subnet

    @checked
    def _removeSubnet(self : Self, subnet : Subnet) -> None:
        """Drop a subnet entirely (detach from its net, drop from index)."""
        self._detachSubnetFromNet(subnet)
        self._subnets.pop(subnet.id, None)

    @checked
    def _addNodesToSubnet(
        self : Self,
        subnet : Subnet,
        nodes : NodeItem | set[NodeItem]
    ) -> None:
        if isinstance(nodes, NodeItem):
            nodes = {nodes}
        subnet.nodes |= nodes
        for node in nodes:
            self._node2subnet[node] = subnet.id

    def _removeNodeFromSubnet(self : Self, node : NodeItem, subnet : Subnet) -> None:
        subnet.nodes.discard(node)
        if not subnet.nodes:
            self._removeSubnet(subnet)

    @checked
    def _resolveSubnets(
        self    : Self,
        subnets : Subnet | list[Subnet] | set[Subnet]
    ) -> None:
        if isinstance(subnets, Subnet):
            subnets = [subnets]
        for subnet in subnets:
            self._resolveSubnet(subnet)

    @checked
    def _resolveSubnet(
        self   : Self,
        subnet : Subnet,
        trail  : list[int] | None = None
    ) -> None:
        # process recursion trail
        if trail is None:
            trail = []
        if subnet.id in trail:
            return
        trail.append(subnet.id)
        tapped_subnets : set[int] = set()
        # gather names from nodes
        label_names   : list[str] = []
        tap_names     : list[str] = []
        i_port_names  : list[str] = []
        io_port_names : list[str] = []
        o_port_names  : list[str] = []
        pin_names     : list[tuple[str, str] | str] = []
        for node in subnet.nodes:
            # labels
            for child in node.childItems():
                if isinstance(child, NetLabelItem):  # label
                    if child.name() == "Name":  # this is a *Name* label
                        label_names.append(child.value())
            # taps (minor end)
            if isinstance(node, TapMinorNodeItem):
                tap : TapItem | None = node.parentItem()
                tap_major_node = tap.majorNode()
                if tap_major_node not in self._node2subnet:
                    continue
                tap_major_subnet_id = self._node2subnet[tap_major_node]
                tap_major_subnet = self._subnets[tap_major_subnet_id]
                tap_major_subnet_name = tap_major_subnet.name
                if tap_major_subnet_name is None:
                    continue
                tap_major_subnet_suffix = tap_major_subnet.suffix
                if tap_major_subnet_suffix is None:
                    continue
                tap_names.append(tap_major_subnet_name)
            # taps (major end)
            elif isinstance(node, TapMajorNodeItem):
                tap : TapItem | None = node.parentItem()
                tap_minor_node = tap.minorNode()
                if tap_minor_node not in self._node2subnet:
                    continue
                tapped_subnets.add(self._node2subnet[tap_minor_node])
            # ports and pins
            elif isinstance(node, FixedNodeItem):
                node_parent = node.parentItem()
                if isinstance(node_parent, PortItem):
                    port_name = node_parent.name()
                    port_direction = node_parent.direction()
                    if port_direction == Direction.IN:
                        i_port_names.append(port_name)
                    elif port_direction == Direction.BI:
                        io_port_names.append(port_name)
                    elif port_direction == Direction.OUT:
                        o_port_names.append(port_name)
                elif isinstance(node_parent, BlockPinItem | SymbolPinItem):
                    pin_parent = node_parent.parentItem()
                    if isinstance(pin_parent, BlockItem | SymbolItem):
                        pin_names.append((pin_parent.label(), node_parent.name()))
        # sort pin name tuples
        if pin_names:
            pin_names.sort(key=lambda x: (x[0], x[1]))
        # convert pin name tuples to single strings
        pin_names = \
            [f"{label}_{name}" for label, name in pin_names]
        # aggregate names
        all_names = \
            label_names + tap_names + \
            i_port_names + io_port_names + o_port_names + \
            pin_names
        # resolve
        resolved_name = None
        resolved_suffix = None
        if all_names:
            name_parts : list[tuple[str, str]] = []
            for name in all_names:
                name_parts.append(_baseNameAndSuffix(name))
            resolved_name = name_parts[0][0]
            scalar_count = 0
            member_count = 0
            vector_count = 0
            for _, suffix in name_parts:
                if   ":" in suffix : vector_count += 1
                elif suffix != ""  : member_count += 1
                else               : scalar_count += 1
            if scalar_count and not (member_count or vector_count):
                resolved_suffix = ""
            elif member_count and not (scalar_count or vector_count):
                # ensure all indices are the same (identical expression)
                if all(s == name_parts[0][1] for _, s in name_parts):
                    resolved_suffix = name_parts[0][1]
            elif vector_count and not (scalar_count or member_count):
                # ensure all ranges have the same width and direction
                def _delta(range_l : int, range_r : int) -> int:
                    return range_l - range_r
                ranges : list[tuple[int, int]] = []
                consistent = True
                for _, suffix in name_parts:
                    range_l_str, range_r_str = suffix.split(':')
                    range_l = evaluate(range_l_str)
                    range_r = evaluate(range_r_str)
                    ranges.append((range_l, range_r))
                    if len(ranges) > 1 \
                    and _delta(*ranges[-1]) != _delta(*ranges[0]):
                        consistent = False
                        break
                if consistent:
                    resolved_suffix = name_parts[0][1]
        # update subnet, recording previous name and suffix
        old_name      = subnet.name
        old_suffix    = subnet.suffix
        subnet.name   = resolved_name
        subnet.suffix = resolved_suffix
        # propagate to net layer
        if resolved_name != old_name:
            # name change => migrate subnet to a different net
            if resolved_name in self._nets:
                new_net = self._nets[resolved_name]
            else:
                new_net = Net(resolved_name, resolved_suffix)
                net_key = subnet.id if resolved_name is None else resolved_name
                self._nets[net_key] = new_net
            self._detachSubnetFromNet(subnet)
            self._attachSubnetToNet(subnet, new_net)
            self._refreshNet(new_net)
        elif old_suffix != resolved_suffix:
            # no name change, suffix change => just refresh the current net
            self._refreshNet(subnet.net)
        # resolve tapped subnets
        for subnet_id in tapped_subnets:
            self._resolveSubnet(self._subnets[subnet_id], trail)

    # -- net helpers -------------------------------------------------------

    @checked
    def _attachSubnetToNet(self : Self, subnet : Subnet, net : Net) -> None:
        subnet.net = net
        net.subnets.add(subnet.id)
        net_key = subnet.id if net.name is None else net.name
        self._subnet2net[subnet.id] = net_key

    @checked
    def _detachSubnetFromNet(self : Self, subnet : Subnet) -> None:
        """Remove `subnet` from its current net, deleting the net if empty."""
        self._subnet2net.pop(subnet.id)
        net = subnet.net
        net.subnets.discard(subnet.id)
        if not net.subnets:
            # remove empty net
            net_key = subnet.id if net.name is None else net.name
            self._nets.pop(net_key)
        subnet.net = None

    @checked
    def _refreshNet(self : Self, net : Net) -> None:
        """Recompute `net.suffix` from its member subnets.

        Vector wins (its span is the bus span); else members; else scalar.
        Falls back to None if any member is unresolved.
        """
        suffixes = [self._subnets[sid].suffix for sid in net.subnets]
        if not suffixes or any(s is None for s in suffixes):
            net.suffix = None
            return
        vec = next((s for s in suffixes if s and ":" in s), None)
        if vec is not None:
            net.suffix = vec
        elif all(s == "" for s in suffixes):
            net.suffix = ""
        else:
            net.suffix = next((s for s in suffixes if s != ""), "")


    # -- serialisation/deserialisation helpers ------------------------------

    @checked
    def _orderedSubnetSegments(
        self: Self,
        subnet: Subnet,
    ) -> list["SegmentItem"]:
        """
        Order subnet edges so each segment shares a node with the previous one.

        Attempts to find an ordering that corresponds to an Eulerian path in the
        subgraph (each segment shares exactly one node with the previous). Falls
        back to arbitrary order (with a warning) if no such chain exists.
        """
        edge_list: list[tuple[NodeItem, NodeItem, "SegmentItem"]] = [
            (u, v, data["segment"])
            for u, v, data in self._graph.subgraph(subnet.nodes).edges(data=True)
        ]
        if not edge_list:
            return []

        # Fast rejection: >2 odd-degree nodes ⇒ no Eulerian path is possible
        degree: dict[NodeItem, int] = {}
        for u, v, _ in edge_list:
            degree[u] = degree.get(u, 0) + 1
            degree[v] = degree.get(v, 0) + 1
        odd_count = sum(1 for d in degree.values() if d % 2 == 1)
        if odd_count > 2:
            logger().warning(
                f"Could not chain segments for subnet {subnet.id}; "
                "emitting in arbitrary order."
            )
            return [seg for _, _, seg in edge_list]

        ordered: list["SegmentItem"] = []
        remaining = list(edge_list)

        def chain(tip: "NodeItem | None") -> bool:
            """Backtracking search for a chain that consumes all remaining edges."""
            if not remaining:
                return True

            n = len(remaining)
            for i in range(n):
                u, v, seg = remaining[i]
                if tip is None:
                    next_tips: tuple["NodeItem", ...] = (v, u)
                elif tip == u:
                    next_tips = (v,)
                elif tip == v:
                    next_tips = (u,)
                else:
                    continue

                # O(1) removal via swap-with-last
                remaining[i], remaining[-1] = remaining[-1], remaining[i]
                popped = remaining.pop()

                ordered.append(seg)
                for new_tip in next_tips:
                    if chain(new_tip):
                        return True

                # backtrack
                ordered.pop()
                remaining.append(popped)
                remaining[i], remaining[-1] = remaining[-1], remaining[i]

            return False

        if chain(None):
            return ordered

        logger().warning(
            f"Could not chain segments for subnet {subnet.id}; "
            "emitting in arbitrary order."
        )
        return [seg for _, _, seg in edge_list]

    @checked
    def _segmentFromXml(
        self        : Self,
        xr          : QXmlStreamReader,
        node_by_id  : dict[int, NodeItem]
    ) -> None:
        nodes_str = xr.attributes().value("Nodes")
        node_id1, node_id2 = (
            int(part) for part in nodes_str.split(",")
        )
        node1 = node_by_id.get(node_id1)
        node2 = node_by_id.get(node_id2)
        if node1 is None:
            logger().warning(f"Segment node 1 (id {node_id1}) missing")
            return
        if node2 is None:
            logger().warning(f"Segment node 2 (id {node_id2}) missing")
            return
        self._scene.addSegment(
            node1.scenePos(),
            node2.scenePos(),
            undoable=False
        )

# -- misc helpers ------------------------------------------------------

@checked
def _baseNameAndSuffix(full_name : str) -> tuple[str, str]:
    if "[" not in full_name:
        return full_name.replace(" ", ""), ""
    base_name = full_name.split('[')[0].replace(" ", "")
    suffix = full_name.split('[')[1].split(']')[0]
    return base_name, suffix
