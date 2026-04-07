import re
from typing import Self
from dataclasses import dataclass, field

import networkx
from networkx.classes.reportviews import NodeView

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...items.vertex  import VertexItem
    from ...items.segment import SegmentItem


def parse_net_name(name : str) -> tuple[str, tuple[int, int] | None]:
    """Parse 'DATA(31:0)' -> ('DATA', (31, 0)).  'CLK' -> ('CLK', None)."""
    m = re.match(r'^(.+?)\((\d+):(\d+)\)$', name)
    if m:
        return m.group(1), (int(m.group(2)), int(m.group(3)))
    return name, None


@dataclass
class ScalarNet:
    name      : str
    vertices  : set["VertexItem"] = field(default_factory=set)
    data_type : "str | VectorNet" = ""  # empty string = default type


@dataclass
class VectorNet:
    name      : str
    vertices  : set["VertexItem"] = field(default_factory=set)
    members   : dict[int, ScalarNet] = field(default_factory=dict)
    data_type : str = ""  # empty string = default type


class Netlist:
    _graph : networkx.Graph
    _nets  : dict[str, ScalarNet | VectorNet]

    def __init__(self : Self) -> None:
        self._graph = networkx.Graph()
        self._nets = {}

    # -- Graph: vertex operations ------------------------------------------

    def addVertex(self : Self, vtx : "VertexItem") -> None:
        self._graph.add_node(vtx)

    def removeVertex(self : Self, vtx : "VertexItem") -> None:
        self._graph.remove_node(vtx)

    def hasVertex(self : Self, vtx : "VertexItem") -> bool:
        return vtx in self._graph

    def vertices(self : Self) -> NodeView:
        return self._graph.nodes

    # -- Graph: segment (edge) operations ----------------------------------

    def addSegment(
        self : Self,
        vtx1 : "VertexItem",
        vtx2 : "VertexItem",
        seg  : "SegmentItem"
    ) -> None:
        self._graph.add_edge(vtx1, vtx2, segment=seg)

    def removeSegment(
        self : Self,
        vtx1 : "VertexItem",
        vtx2 : "VertexItem"
    ) -> None:
        self._graph.remove_edge(vtx1, vtx2)

    def hasSegment(
        self : Self,
        vtx1 : "VertexItem",
        vtx2 : "VertexItem"
    ) -> bool:
        return self._graph.has_edge(vtx1, vtx2)

    # -- Graph: queries ----------------------------------------------------

    def degree(self : Self, vtx : "VertexItem") -> int:
        """Number of segments connected to the vertex."""
        return self._graph.degree(vtx)

    def segments(self : Self, vtx : "VertexItem") -> list["SegmentItem"]:
        """Segments connected to the vertex."""
        return [
            data["segment"]
            for _, _, data in self._graph.edges(vtx, data=True)
        ]

    def physicalNet(self : Self, vtx : "VertexItem") -> set["VertexItem"]:
        """Connected component containing the vertex."""
        return set(networkx.node_connected_component(self._graph, vtx))

    def hasPath(
        self : Self,
        vtx1 : "VertexItem",
        vtx2 : "VertexItem"
    ) -> bool:
        return networkx.has_path(self._graph, vtx1, vtx2)

    # -- Logical netlist ---------------------------------------------------

    def net(self : Self, name : str) -> ScalarNet | VectorNet | None:
        """Look up a net by name."""
        return self._nets.get(name)

    def netType(self : Self, name : str) -> str:
        """Resolve the type code for a net, following bus reference."""
        entry = self._nets.get(name)
        if entry is None:
            return ""
        if isinstance(entry, VectorNet):
            return entry.data_type
        if isinstance(entry.data_type, VectorNet):
            return entry.data_type.data_type
        return entry.data_type

    def netVertices(self : Self, name : str) -> set["VertexItem"]:
        """All vertices belonging to a net (own + bus-level for members)."""
        entry = self._nets.get(name)
        if entry is None:
            return set()
        if isinstance(entry, ScalarNet) and isinstance(entry.data_type, VectorNet):
            return entry.vertices | entry.data_type.vertices
        return set(entry.vertices)

    def logicalNet(self : Self, name : str) -> set["VertexItem"]:
        """Expand a net's vertices to full connected components."""
        result = set()
        for vtx in self.netVertices(name):
            result |= set(networkx.node_connected_component(self._graph, vtx))
        return result
