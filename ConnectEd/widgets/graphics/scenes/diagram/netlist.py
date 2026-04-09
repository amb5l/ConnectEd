import re
import networkx

from typing      import Any, Self
from dataclasses import dataclass, field
from enum        import StrEnum

from PyQt6.QtCore import QXmlStreamWriter, QXmlStreamReader

from ...items.node           import NodeItem
from ...items.entry          import EntryItem
from ...items.vertex         import VertexItem
from ...items.port           import PortItem
from ...items.property_label import PropertyLabelItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...items.segment import SegmentItem

class NetCategory(StrEnum):
    UNRESOLVED = "unresolved"
    SCALAR     = "scalar"
    MEMBER     = "member"
    VECTOR     = "vector"


@dataclass(slots=True)
class Net:
    id        : int
    category  : NetCategory = NetCategory.UNRESOLVED
    name      : str | None = None # resolved name or None
    vector    : "Net | None" = None # member's vector
    members   : list["Net"] = field(default_factory=list)  # vector's members
    nodes     : set[NodeItem] = field(default_factory=set)

    def isUnresolved(self : Self) -> bool:
        return self.category == NetCategory.UNRESOLVED

    def isScalar(self : Self) -> bool:
        return self.category == NetCategory.SCALAR

    def isMember(self : Self) -> bool:
        return self.category == NetCategory.MEMBER

    def isVector(self : Self) -> bool:
        return self.category == NetCategory.VECTOR

    def memberNets(self : Self) -> list["Net"]:
        return self.children if self.isVector() else []


shit
two different nets exist
they are labelled
user changes a label => merges the nets

detect conflicting ranges on bus name labels in the same physical net

class Netlist:
    _graph    : networkx.Graph
    _nets     : dict[int, Net]                # net ID : net instance
    _node2net : dict[NodeItem, int | None]  # node instance : net ID
    _id       : int                           # net ID counter

    def __init__(self : Self) -> None:
        self._graph = networkx.Graph()
        self._nets = {}
        self._node2net = {}
        self._id = 0

    # -- Graph: vertex operations ------------------------------------------

    def addNode(self : Self, node : NodeItem) -> None:
        self._graph.add_node(node)
        self._node2net[node] = None

    def removeNode(self : Self, node : NodeItem) -> None:
        self._graph.remove_node(node)
        if node in self._node2net:
            net_id = self._node2net[node]
            if net_id is not None:
                net = self._nets[net_id]
                net.nodes.remove(node)
            self._node2net.pop(node)

    def hasNode(self : Self, node : NodeItem) -> bool:
        return node in self._node2net

    def nodes(self : Self) -> list[NodeItem]:
        return self._node2net.keys()

    # -- Graph: segment (edge) operations ----------------------------------

    def addSegment(
        self : Self,
        node1 : NodeItem,
        node2 : NodeItem,
        seg  : "SegmentItem"
    ) -> None:
        net_id1 = self._node2net[node1]
        net_id2 = self._node2net[node2]
        net1 = self._nets[net_id1]
        net2 = self._nets[net_id2]
        self._graph.add_edge(node1, node2, segment=seg)
        if net1 is None:
            if net2 is None:
                # 2 new nodes => new net
                net = self.newNet()
                net.nodes.add(node1)
                net.nodes.add(node2)
                self._node2net[node1] = net.id
                self._node2net[node2] = net.id
                self._resolveNet(net)
            else:
                # node1 is new, node2 is part of a net => merge node1 into net2
                net2.nodes.add(node1)
                self._node2net[node1] = net2.id
                self._resolveNet(net2)
        else:
            if net2 is None:
                # node2 is new, node1 is part of a net => merge node2 into net1
                net1.nodes.add(node2)
                self._node2net[node2] = net1.id
                self._resolveNet(net1)
            else:
                if net1 is not net2:
                    # both vertices are part of different nets => merge nets
                    net1.nodes |= net2.nodes
                    for vtx in net2.nodes:
                        self._node2net[vtx] = net1.id
                    self._nets.pop(net2.id)
                    self._resolveNet(net1)
                else:
                    # both vertices are part of the same net => do nothing
                    pass

    def removeSegment(
        self : Self,
        node1 : NodeItem,
        node2 : NodeItem
    ) -> None:
        # remove edge from graph
        self._graph.remove_edge(node1, node2)
        # check for net split
        if networkx.has_path(self._graph, node1, node2):
            return  # net has not been split
        # split net
        net_id1 = self._node2net[node1]
        net1 = self._nets[net_id1]
        net2 = self.newNet()
        nodes2 : set[NodeItem] = set()
        for vtx in net1.nodes:
            if node is node2 or networkx.has_path(self._graph, node, node2):
                nodes2.add(node)
        for node in nodes2:
            net1.nodes.remove(vtx)
            net2.nodes.add(vtx)
            self._node2net[vtx] = net2.id
        self._resolveNet(net1)
        self._resolveNet(net2)

    def hasSegment(
        self : Self,
        node1 : NodeItem,
        node2 : NodeItem
    ) -> bool:
        return self._graph.has_edge(node1, node2)

    # -- Graph: queries ----------------------------------------------------

    def degree(self : Self, node : NodeItem) -> int:
        """Number of segments connected to the node."""
        return self._graph.degree(vtx)

    def edges(self : Self, node : NodeItem) -> list["SegmentItem"]:
        """Edges connected to the node."""
        iterator = self._graph.edges(vtx, data=True)
        return [data["segment"] for _, _, data in iterator]

    def physicalNet(self : Self, node : NodeItem) -> set[NodeItem]:
        """Connected component containing the node."""
        return set(networkx.node_connected_component(self._graph, vtx))

    def hasPath(self : Self, node1 : NodeItem, node2 : NodeItem) -> bool:
        return networkx.has_path(self._graph, node1, node2)

    # -- Logical netlist ---------------------------------------------------

    def newNet(self : Self) -> Net:
        """Create a new net."""
        net = Net(id=self._id)
        self._id += 1
        self._nets[net.id] = net
        return net

    # -- Serialisation -----------------------------------------------------

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        # start
        xw.writeStartElement("Connectivity")
        # nodes: entries, vertices and PropertyLabelItem instances
        raw_nodes : list[NodeItem] = self._node2net.keys()
        entries : list[EntryItem] = [
            node for node in raw_nodes if isinstance(node, EntryItem)
        ]
        vertices : list[VertexItem] = [
            node for node in raw_nodes if isinstance(node, VertexItem)
        ]
        nodes = entries + vertices  # entries then vertices
        for id, node in enumerate(raw_nodes):
            node.toXml(xw, id)
        # physical nets (segment groups)
        groups : list[str] = []
        vtx2gid : dict[VertexItem, int] = {}
        for component in networkx.connected_components(self._graph):
            gid = len(groups)
            for vtx in component:
                vtx2gid[vtx] = gid
            subgraph = self._graph.subgraph(component)
            vertex_pairs = [
                f"{nodes.index(v1)},{nodes.index(v2)}"
                     for v1, v2 in subgraph.edges()
            ]
            groups.append(" ".join(vertex_pairs))
        for id, segments in enumerate(groups):
            xw.writeStartElement("PhysicalNet")
            xw.writeAttribute("ID", str(id))
            xw.writeAttribute("Segments", segments)
            xw.writeEndElement()
        # write logical nets
        for net in self._nets.values():
            tag = net.__class__.__name__
            xw.writeStartElement(tag)
            if net.name is not None:
                xw.writeAttribute("Name", net.name)
            if isinstance(net, VectorNet) or \
               (isinstance(net, ScalarNet) and isinstance(net.data_type, str)):
                if net.data_type:
                    xw.writeAttribute("Type", net.data_type)
            gids = sorted({vtx2gid[v] for v in net.nodes if v in vtx2gid})
            xw.writeAttribute("PhysicalNets", " ".join(str(gid) for gid in gids))
            if isinstance(net, VectorNet):
                for idx, member in net.members.items():
                    if not member.vertices:  # skip members with no vertices
                        continue
                    xw.writeStartElement("Member")
                    xw.writeAttribute("Index", str(idx))
                    mpids = sorted(
                        {vtx2pnet[v] for v in member.vertices if v in vtx2pnet}
                    )
                    xw.writeAttribute(
                        "PhysicalNets", " ".join(str(p) for p in mpids)
                    )
                    xw.writeEndElement()
            xw.writeEndElement()
        # end
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        # TODO: update _id to be greated than any net ID in the XML
        instance = cls()
        return instance

    # -- Private helpers ---------------------------------------------------


    def _resolveNet(self : Self, net : Net) -> None:
        vertices = net.nodes
        label_names = []
        port_names = []
        for vtx in vertices:
            parent = vtx.parentItem()
            if isinstance(vtx, EntryItem):  # entry
                if isinstance(parent, PortItem):  # port entry
                    port_names.append(parent.name())
            elif isinstance(vtx, VertexItem):  # free vertex
                for child in vtx.childItems():
                    if isinstance(child, PropertyLabelItem): # label
                        if child.name() == "Name":  # name label
                            label_names.append(child.value())
        all_names = label_names + port_names
        vector_names = []
        member_names = []
        scalar_names = []
        category = NetCategory.UNRESOLVED
        name = None
        for name in all_names:
            if clean_name := self._cleanVectorName(name):
                vector_names.append(clean_name)
            elif clean_name := self._cleanMemberName(name):
                member_names.append(clean_name)
            elif clean_name := self._cleanScalarName(name):
                scalar_names.append(clean_name)
        if vector_names and not (member_names or scalar_names):
            # sort vector names from widest to narrowest range
            # don't bother if any alphas appear in the ranges
            shit
            resolved_name = vector_names[0]
        elif member_names and not (vector_names or scalar_names):
            shit look for inconsistent indices
            resolved_name = member_names[0]
        elif scalar_names and not (vector_names or member_names):
            resolved_name = scalar_names[0]


        if len(label_names) > 0:
            if len(label_names) == 1 \
            or all(label == label_names[0] for label in label_names):
                name = label_names[0]
        elif len(port_names) > 0:
            if len(port_names) == 1 \
            or all(port == port_names[0] for port in port_names):
                name = port_names[0]
        net.name = name

    def _validBaseName(self, name: str) -> bool:
        """Check if base name follows the safe cross-HDL rule we defined earlier:
        starts with a letter, then letters/digits or single underscores only,
        never two underscores in a row, never ends with an underscore.
        """
        if not name:
            return False
        # This regex enforces the exact rule (no __, no trailing _)
        return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9]*(?:_[a-zA-Z0-9]+)*$', name))

    def _validExpression(self, expr: str) -> bool:
        """Simple but effective validation for index/range expressions.
        Accepts integers or expressions using only the allowed operators
        (+, -, *, /, **), parentheses, alphanumeric characters (for parameters
        like WIDTH), underscores, and whitespace.
        """
        if not expr:
            return False
        # Remove ** first so consecutive * characters are valid
        cleaned = expr.replace('**', '')
        # Only allowed characters
        if re.search(r'[^a-zA-Z0-9_+\-*/()\s]', cleaned):
            return False
        # Quick balanced-parentheses check (catches most obvious errors)
        if cleaned.count('(') != cleaned.count(')'):
            return False
        return True

    def _vectorNameRange(self, name: str) -> tuple[str, str] | None:
        name = name.strip()
        if '[' not in name or not name.endswith(']'):
            return None
        bracket_start = name.rfind('[')
        base = name[:bracket_start].strip()
        if not self._validBaseName(base):
            return None
        range = name[bracket_start+1:-1].strip()
        if range.count(':') != 1:
            return None
        left, right = [p.strip() for p in range.split(':', 1)]
        if not self._validExpression(left) \
        or not self._validExpression(right):
            return None
        return base, range

    def _cleanVectorName(self, name: str) -> str | None:
        """Returns clean vector name or None. """
        base, range = self._vectorNameRange(name)
        return f"{base}[{range}]"

    def _memberNameIndex(self, name: str) -> tuple[str, str] | None:
        name = name.strip()
        if '[' not in name or not name.endswith(']'):
            return None
        bracket_start = name.rfind('[')
        base = name[:bracket_start].strip()
        if not self._validBaseName(base):
            return None
        index = name[bracket_start+1:-1].strip()
        if ':' in index or not self._validExpression(index):
            return None
        return base, index

    def _cleanMemberName(self, name: str) -> str | None:
        """Returns clean member name or None."""
        base, index = self._memberNameIndex(name)
        return f"{base}[{index}]"

    def _cleanScalarName(self, name: str) -> str | None:
        """Returns clean scalar name or None. """
        name = name.strip()
        if self._validBaseName(name):
            return name
        return None
