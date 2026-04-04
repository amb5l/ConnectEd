from typing import Self

from PyQt6.QtCore import QPointF

from ....items.vertex  import VertexItem
from ....items.segment import SegmentItem

from . import CmdSceneBase

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class CmdAddVertex(CmdSceneBase):
    """
    Create and add a new vertex to the scene.
    Updates both graphics and graph.
    Assumption: no existing vertices or segments at this point.
    """

    # instance attributes
    _vtx : VertexItem

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        pos   : QPointF
    ) -> None:
        super().__init__(scene)
        self._vtx = VertexItem(pos)

    def redo(self : Self) -> None:
        self._scene.addItem(self._vtx)
        self._scene._graph.add_node(self._vtx)

    def undo(self : Self) -> None:
        self._scene._graph.remove_node(self._vtx)
        self._scene.removeItem(self._vtx)

    def vtx(self : Self) -> VertexItem:
        return self._vtx


class CmdRemoveVertex(CmdSceneBase):
    """
    Remove a specified vertex from the scene.
    Updates both graphics and graph.
    Assumption: vertex has no edges in the graph.
    """

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
        self._scene._graph.remove_node(self._vtx)
        self._scene.removeItem(self._vtx)

    def undo(self : Self) -> None:
        self._scene.addItem(self._vtx)
        self._scene._graph.add_node(self._vtx)


class CmdAddSegment(CmdSceneBase):
    """
    Add a new segment to the scene between two specified vertices.
    Updates both graphics and graph.
    Assumption: does not cross other vertices.
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
        self._seg.setVtx1(self._vtx1)
        self._seg.setVtx2(self._vtx2)
        self._scene.addItem(self._seg)
        self._scene._graph.add_edge(
            self._vtx1, self._vtx2, segment=self._seg)
        self._vtx1.onConnectionChange()
        self._vtx2.onConnectionChange()

    def undo(self : Self) -> None:
        self._scene._graph.remove_edge(self._vtx1, self._vtx2)
        self._vtx1.onConnectionChange()
        self._vtx2.onConnectionChange()
        self._seg.setVtx1(None)
        self._seg.setVtx2(None)
        self._scene.removeItem(self._seg)

    def seg(self : Self) -> SegmentItem:
        return self._seg


class CmdRemoveSegment(CmdSceneBase):
    """
    Remove a specified segment from the scene.
    Updates both graphics and graph.
    Does not remove vertices; the API layer may follow with
    CmdRemoveVertex for any orphaned vertices.
    """

    # instance attributes
    _vtx1 : VertexItem
    _vtx2 : VertexItem
    _seg  : SegmentItem

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        seg   : SegmentItem
    ) -> None:
        super().__init__(scene)
        self._vtx1 = seg.vtx1()
        self._vtx2 = seg.vtx2()
        self._seg = seg

    def redo(self : Self) -> None:
        self._scene._graph.remove_edge(self._vtx1, self._vtx2)
        self._vtx1.onConnectionChange()
        self._vtx2.onConnectionChange()
        self._seg.setVtx1(None)
        self._seg.setVtx2(None)
        self._scene.removeItem(self._seg)

    def undo(self : Self) -> None:
        self._seg.setVtx1(self._vtx1)
        self._seg.setVtx2(self._vtx2)
        self._scene.addItem(self._seg)
        self._scene._graph.add_edge(self._vtx1, self._vtx2, segment=self._seg)
        self._vtx1.onConnectionChange()
        self._vtx2.onConnectionChange()


class CmdSplitSegment(CmdSceneBase):
    """Split a segment at a vertex. Updates both graphics and graph."""

    # instance attributes
    _vtx      : VertexItem   # vertex at split point
    _vtx1     : VertexItem   # original near vertex of seg1
    _vtx2     : VertexItem   # original far vertex of seg1
    _seg1     : SegmentItem  # existing segment (shortened to vtx1--vtx)
    _seg2     : SegmentItem  # new segment (vtx--vtx2)

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        seg   : SegmentItem,
        vtx   : VertexItem
    ) -> None:
        super().__init__(scene)
        self._vtx = vtx
        self._vtx1 = seg.vtx1()
        self._vtx2 = seg.vtx2()
        self._seg1 = seg
        self._seg2 = SegmentItem()

    def redo(self : Self) -> None:
        # graph: remove original edge, add two new edges
        self._scene._graph.remove_edge(self._vtx1, self._vtx2)
        self._scene._graph.add_edge(self._vtx1, self._vtx, segment=self._seg1)
        self._scene._graph.add_edge(self._vtx, self._vtx2, segment=self._seg2)
        # graphics: shorten seg1, create seg2
        self._seg2.setVtx1(self._vtx)
        self._seg2.setVtx2(self._vtx2)
        self._seg1.setVtx2(self._vtx)
        self._scene.addItem(self._seg2)
        self._vtx.onConnectionChange()
        self._vtx1.onConnectionChange()
        self._vtx2.onConnectionChange()

    def undo(self : Self) -> None:
        # graph: remove two edges, restore original edge
        self._scene._graph.remove_edge(self._vtx1, self._vtx)
        self._scene._graph.remove_edge(self._vtx, self._vtx2)
        self._scene._graph.add_edge(self._vtx1, self._vtx2, segment=self._seg1)
        # graphics: restore seg1, remove seg2
        self._seg1.setVtx2(self._vtx2)
        self._seg2.setVtx1(None)
        self._seg2.setVtx2(None)
        self._scene.removeItem(self._seg2)
        self._vtx.onConnectionChange()
        self._vtx1.onConnectionChange()
        self._vtx2.onConnectionChange()


class CmdUnsplitSegment(CmdSceneBase):
    """
    Unsplit a segment at a specified vertex. Updates both graphics and
    graph. Assumption: vertex has exactly 2 graph edges.
    """

    # instance attributes
    _vtx  : VertexItem   # vertex being removed
    _far1 : VertexItem   # far vertex of seg1
    _far2 : VertexItem   # far vertex of seg2
    _seg1 : SegmentItem  # surviving segment (far1--far2 after redo)
    _seg2 : SegmentItem  # removed segment

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        vtx   : VertexItem
    ) -> None:
        super().__init__(scene)
        self._vtx = vtx
        segs = vtx.segments()
        self._seg1 = segs[0]
        self._seg2 = segs[1]
        self._far1 = self._seg1.otherVtx(vtx)
        self._far2 = self._seg2.otherVtx(vtx)

    def redo(self : Self) -> None:
        # graph: remove two edges and node, add merged edge
        self._scene._graph.remove_edge(self._far1, self._vtx)
        self._scene._graph.remove_edge(self._vtx, self._far2)
        self._scene._graph.remove_node(self._vtx)
        self._scene._graph.add_edge(
            self._far1, self._far2, segment=self._seg1)
        # graphics: extend seg1 to span far1--far2, remove seg2
        self._seg1.changeVtx(self._vtx, self._far2)
        self._seg2.setVtx1(None)
        self._seg2.setVtx2(None)
        self._scene.removeItem(self._seg2)
        self._far1.onConnectionChange()
        self._far2.onConnectionChange()

    def undo(self : Self) -> None:
        # graph: remove merged edge, restore node and two edges
        self._scene._graph.remove_edge(self._far1, self._far2)
        self._scene._graph.add_node(self._vtx)
        self._scene._graph.add_edge(
            self._far1, self._vtx, segment=self._seg1)
        self._scene._graph.add_edge(
            self._vtx, self._far2, segment=self._seg2)
        # graphics: shorten seg1 back, restore seg2
        self._seg1.changeVtx(self._far2, self._vtx)
        self._seg2.setVtx1(self._vtx)
        self._seg2.setVtx2(self._far2)
        self._scene.addItem(self._seg2)
        self._far1.onConnectionChange()
        self._far2.onConnectionChange()
        self._vtx.onConnectionChange()
