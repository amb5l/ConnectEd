from typing      import Self

from PyQt6.QtCore import QPointF

from ......app import logger

from ....items.vertex  import VertexItem
from ....items.segment import SegmentItem

from ..conn import NetEdge

from . import CmdSceneBase

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class CmdAddVertex(CmdSceneBase):
    """
    Create and add a new vertex to the scene.
    Split any crossing segment(s) and join their net(s).
    """

    # instance attributes
    _vtx : VertexItem

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        pos   : QPointF
    ) -> None:
        super().__init__(scene)
        self._vtx = VertexItem(pos, scene._id_vtx.next())

    def redo(self : Self) -> None:
        self._scene.addItem(self._vtx)

    def undo(self : Self) -> None:
        self._scene.removeItem(self._vtx)

    def vtx(self : Self) -> VertexItem:
        return self._vtx


class CmdRemoveVertex(CmdSceneBase):
    """Remove a specified vertex from the scene."""

    # instance attributes
    _vtx : VertexItem

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        vtx   : VertexItem
    ) -> None:
        super().__init__(scene)
        self._vtx = vtx

    def redo(self : Self) -> None:
        self._scene.removeItem(self._vtx)

    def undo(self : Self) -> None:
        self._scene.addItem(self._vtx)


class CmdAddSegment(CmdSceneBase):
    """
    Add a new segment to the scene between two specified vertices:
    -
    """

    # instance attributes
    _vtx1 : VertexItem
    _vtx2 : VertexItem
    _seg  : SegmentItem

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        vtx1  : VertexItem,
        vtx2  : VertexItem
    ) -> None:
        super().__init__(scene)
        self._vtx1 = vtx1
        self._vtx2 = vtx2
        self._seg = SegmentItem()

    def redo(self : Self) -> None:
        # attach segment to vertices
        self._seg.setVtx1(self._vtx1)
        self._seg.setVtx2(self._vtx2)
        # add segment to scene
        self._scene.addItem(self._seg)

    def undo(self : Self) -> None:
        # detach segment from vertices
        self._seg.setVtx1(None)
        self._seg.setVtx2(None)
        # remove segment from scene
        self._scene.removeItem(self._seg)

    def seg(self : Self) -> SegmentItem:
        return self._seg


class CmdReattachSegment(CmdSceneBase):
    """
    Detach a segment from one vertex and attach it to another.
    """

    # instance attributes
    _seg     : SegmentItem
    _vtx_old : VertexItem
    _vtx_new : VertexItem

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        seg     : SegmentItem,
        vtx_old : VertexItem,
        vtx_new : VertexItem
    ) -> None:
        super().__init__(scene)
        self._seg = seg
        self._vtx_old = vtx_old
        self._vtx_new = vtx_new

    def redo(self : Self) -> None:
        if not self._seg.reattach(self._vtx_old, self._vtx_new):
            logger().warning(f"Failed to reattach segment {self._seg} to {self._vtx_new}")

    def undo(self : Self) -> None:
        if not self._seg.reattach(self._vtx_new, self._vtx_old):
            logger().warning(f"Failed to reattach segment {self._seg} to {self._vtx_old}")


class CmdRemoveSegment(CmdSceneBase):
    """Remove a specified segment from the scene."""

    # instance attributes
    _vtx1 : VertexItem
    _vtx2 : VertexItem
    _seg  : SegmentItem

    def __init__(
        self : Self,
        scene : "DrawingScene",
        seg : SegmentItem
    ) -> None:
        super().__init__(scene)
        self._vtx1 = seg.vtx1()
        self._vtx2 = seg.vtx2()
        self._seg = seg

    def redo(self : Self) -> None:
        self._seg.setVtx1(None)
        self._seg.setVtx2(None)
        self._scene.removeItem(self._seg)

    def undo(self : Self) -> None:
        self._seg.setVtx1(self._vtx1)
        self._seg.setVtx2(self._vtx2)
        self._scene.addItem(self._seg)


class CmdSplitSegment(CmdSceneBase):
    """Split a segment at a specified vertex."""

    # instance attributes
    _vtx  : VertexItem   # vertex at split point
    _seg1 : SegmentItem  # existing segment
    _seg2 : SegmentItem  # new segment

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        seg   : SegmentItem,
        vtx   : VertexItem
    ) -> None:
        super().__init__(scene)
        self._vtx = vtx
        self._seg1 = seg
        self._seg2 = SegmentItem()

    def redo(self : Self) -> None:
        self._seg2.setVtx1(self._vtx)
        self._seg2.setVtx2(self._seg1.vtx2())
        self._seg1.setVtx2(self._vtx)
        self._scene.addItem(self._seg2)

    def undo(self : Self) -> None:
        self._seg1.setVtx2(self._seg2.vtx2())
        self._seg2.setVtx1(None)
        self._seg2.setVtx2(None)
        self._scene.removeItem(self._seg2)


class CmdUnsplitSegment(CmdSceneBase):
    """
    Unsplit a segment at a specified vertex.
    Assumption: vertex has 2 connections.
    """

    # instance attributes
    _vtx  : VertexItem   # vertex at split point
    _seg1 : SegmentItem  # 1st existing segment / unsplit segment
    _seg2 : SegmentItem  # 2nd existing segment
    _vtx2 : VertexItem   # far vertex of 2nd segment
    _s2v1 : VertexItem   # segment 2 vertex 1
    _s2v2 : VertexItem   # segment 2 vertex 2

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        vtx   : VertexItem
    ) -> None:
        super().__init__(scene)
        self._vtx = vtx
        self._seg1 = vtx.connections()[0]
        self._seg2 = vtx.connections()[1]
        self._vtx2 = self._seg2.otherVtx(vtx)
        self._s2v1 = self._seg2.vtx1()
        self._s2v2 = self._seg2.vtx2()

    def redo(self : Self) -> None:
        self._seg2.setVtx1(None)
        self._seg2.setVtx2(None)
        self._scene.removeItem(self._seg2)
        self._seg1.setVtx(self._vtx, self._vtx2)

    def undo(self : Self) -> None:
        self._seg1.setVtx(self._vtx2, self._vtx)
        self._seg2.setVtx1(self._s2v1)
        self._seg2.setVtx2(self._s2v2)
        self._scene.addItem(self._seg2)


class CmdSplitNetEdge(CmdSceneBase):
    """Split a net edge and insert a new vertex at the split point."""

    # instance attributes
    _edge_net_id : int
    _vtx_net_id  : int | None

    def __init__(
        self   : Self,
        scene  : "DrawingScene",
        edge   : NetEdge,
        vtx_id : int
    ) -> None:
        super().__init__(scene)
        self._net_edge = edge
        self._vtx_id = vtx_id

    def redo(self : Self) -> None:
        self._scene.mergeNetEdgeNode(self._net_edge, self._vtx_id)

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







    def undo(self : Self) -> None:
        self._scene.unSplitNetEdge(self._net_edge, self._vtx_id)
