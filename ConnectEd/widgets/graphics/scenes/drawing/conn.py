from typing      import Self, NamedTuple
from collections import defaultdict

from PyQt6.QtCore    import QXmlStreamWriter, QXmlStreamReader

from .....app import logger

from .....core.types import DataKind, Counter
from .....core.xml   import toXmlAttrs
from .....core.utils import underscore2space

from ...properties import PropertiesMixin, InherentProperty

from ...items.vertex  import VertexItem


class NetEdge(NamedTuple):
    node_id1 : int
    node_id2 : int


class Net(PropertiesMixin):
    # class attributes
    _PROPERTIES = {
        "ID" : InherentProperty(
            kind   = DataKind.INT,
            getter = lambda self: self._id,
            setter = lambda self, value: setattr(self, "_id", value)
        ),
        "Name" : InherentProperty(
            kind   = DataKind.STR,
            worthy = lambda self: self._name is not None and self._name != "",
            getter = lambda self: self.name(),
            setter = lambda self, value: self.setName(value)
        )
    }

    # instance attributes
    _id        : int | None
    _name      : str | None
    _adjacency : dict[int, set[int]]  # node ID : list of neighbour node IDs

    def __init__(
        self : Self,
        id   : int | None = None,
        name : str | None = None
    ) -> None:
        self._id = id
        self._name = "" if name is None else name
        self._adjacency = defaultdict(set)
        self.initProperties()

    def id(self : Self) -> int:
        return self._id

    def name(self : Self) -> str:
        return self._name

    def setName(self : Self, name : str) -> None:
        self._name = name

    def adjacency(self : Self) -> dict[int, set[int]]:
        return self._adjacency

    def setAdjacency(self : Self, adjacency : dict[int, set[int]]) -> None:
        self._adjacency = adjacency

    def hasEdge(self : Self, edge : NetEdge) -> bool:
        return \
                edge.node_id1 in self._adjacency \
            and edge.node_id2 in self._adjacency \
            and edge.node_id2 in self._adjacency[edge.node_id1] \
            and edge.node_id1 in self._adjacency[edge.node_id2]

    def addEdge(self : Self, edge : NetEdge) -> None:
        self._adjacency[edge.node_id1].add(edge.node_id2)
        self._adjacency[edge.node_id2].add(edge.node_id1)

    def splitEdge(self : Self, edge : NetEdge, node_id : int) -> None:
        self._adjacency[edge.node_id1].remove(edge.node_id2)
        self.addEdge(edge.node_id1, node_id)
        self._adjacency[edge.node_id2].remove(edge.node_id1)
        self.addEdge(edge.node_id2, node_id)

    def unSplitEdge(self : Self, edge : NetEdge, node_id : int) -> None:
        self._adjacency[edge.node_id1].remove(node_id)
        self._adjacency[edge.node_id2].remove(node_id)
        self.addEdge(edge)

    def toXml(self, xw : QXmlStreamWriter) -> None:
        # start
        xw.writeStartElement("Net")
        # properties
        toXmlAttrs(self, xw)
        # edges
        pairs = []
        for node_id1, neighbours in self._adjacency.items():
            for node_id2 in neighbours:
                if node_id1 < node_id2:
                    pairs.append(f"{node_id1},{node_id2}")
        if pairs:
            xw.writeAttribute("Edges", " ".join(pairs))
        # end
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        instance : "Net" = cls()
        xml_attrs = xr.attributes()
        for xml_attr in xml_attrs:
            if xml_attr.name() == "Edges":
                pairs = xml_attr.value().split(" ")
                for pair in pairs:
                    s1, s2 = pair.split(",")
                    node_id1, node_id2 = int(s1), int(s2)
                    instance._adjacency[node_id1].add(node_id2)
                    instance._adjacency[node_id2].add(node_id1)
            else:
                instance.properties.init(
                    underscore2space(xml_attr.name()), xml_attr.value()
                )
        xr.readNext()
        return instance


class DrawingSceneConnMixin:
    _id_net   : Counter
    _id_vtx   : Counter
    _nets     : dict[int, Net]         # net ID : net instance
    _node_net : dict[int, int]         # node (vertex) ID : net ID
    _nodes    : dict[int, VertexItem]  # node (vertex) ID : vertex instance

    def initConn(self : Self) -> None:
        self._id_net = Counter()
        self._id_vtx = Counter()
        self._nets = {}
        self._nodes = {}

    def mergeNetEdgeNode(self : Self, edge : NetEdge, node : int) -> bool:
        edge_net_id = self._node_net[edge.node_id1]
        edge_net = self._nets[edge_net_id]
        adjacency = edge_net.adjacency()
        if node in self._node_net:  # node already in a net so merge
            # get node net
            node_net_id = self._node_net[node]
            node_net = self._nets[node_net_id]
            # merge node adjacency into edge adjacency
            adjacency |= node_net.adjacency()
            edge_net.setAdjacency(adjacency)
            # update node ID : net ID dict
            for nodes in node_net.nodes():
                self._node_net[nodes] = edge_net_id
            # remove node net
            del self._nets[node_net_id]
            del node_net
        edge_net.splitEdge(edge, node)
        self._node_net[node] = edge_net_id
