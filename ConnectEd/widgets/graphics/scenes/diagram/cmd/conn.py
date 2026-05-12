from typing import Self

from PyQt6.QtCore import QPointF

from ....items.node    import NodeItem, FreeNodeItem
from ....items.segment import SegmentItem

from ...drawing.cmd import CmdSceneBase

from ..netlist import Net

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DiagramScene


class CmdDiagramSceneBase(CmdSceneBase):
    # instance attributes
    _scene : "DiagramScene"

    def __init__(self : Self, scene : "DiagramScene"):
        super().__init__(scene)


class CmdAddFreeNode(CmdDiagramSceneBase):
    """
    Create and add a new free node to the scene.
    Updates both graphics and graph.
    Assumption: no existing nodes or segments at this point.
    """

    # instance attributes
    _node : FreeNodeItem

    def __init__(
        self  : Self,
        scene : "DiagramScene",
        pos   : QPointF
    ) -> None:
        super().__init__(scene)
        self._node = FreeNodeItem(pos)

    def redo(self : Self) -> None:
        self._scene.addItem(self._node)
        self._scene.netlist.adoptNode(self._node)

    def undo(self : Self) -> None:
        self._scene.netlist.removeNodes(self._node)
        self._scene.removeItem(self._node)

    def node(self : Self) -> FreeNodeItem:
        return self._node


class CmdRemoveFreeNode(CmdDiagramSceneBase):
    """
    Remove a specified free node from the scene.
    Updates both graphics and graph.
    Assumption: free node has no edges in the graph.
    """

    # instance attributes
    _node : FreeNodeItem

    def __init__(
        self  : Self,
        scene : "DiagramScene",
        node  : FreeNodeItem
    ) -> None:
        super().__init__(scene)
        self._node = node

    def redo(self : Self) -> None:
        self._scene.netlist.removeNodes(self._node)
        self._scene.removeItem(self._node)

    def undo(self : Self) -> None:
        self._scene.addItem(self._node)
        self._scene.netlist.adoptNode(self._node)


class CmdReplaceNode(CmdDiagramSceneBase):
    """
    Replace one node with another. Typically used for free/non swaps.
    Updates both graphics and graph.
    """

    _node1 : NodeItem
    _node2 : NodeItem

    def __init__(
        self  : Self,
        scene : "DiagramScene",
        node1 : NodeItem,
        node2 : NodeItem
    ) -> None:
        super().__init__(scene)
        self._node1 = node1
        self._node2 = node2

    def redo(self : Self) -> None:
        self._scene.netlist.replaceNode(self._node1, self._node2)
        self._node2.onConnectionChange()

    def undo(self : Self) -> None:
        self._scene.netlist.replaceNode(self._node2, self._node1)
        self._node1.onConnectionChange()


class CmdAddSegment(CmdDiagramSceneBase):
    """
    Add a new segment to the scene between two specified vertices.
    Updates both graphics and graph.
    Assumption: does not cross other vertices.
    """

    # instance attributes
    _node1 : NodeItem
    _node2 : NodeItem
    _seg   : SegmentItem

    def __init__(
        self  : Self,
        scene : "DiagramScene",
        node1 : NodeItem,
        node2 : NodeItem
    ) -> None:
        super().__init__(scene)
        self._node1 = node1
        self._node2 = node2
        self._seg = SegmentItem()

    def redo(self : Self) -> None:
        self._seg.setNode1(self._node1)
        self._seg.setNode2(self._node2)
        self._scene.addItem(self._seg)
        self._scene.netlist.addSegment(self._seg)
        self._node1.onConnectionChange()
        self._node2.onConnectionChange()

    def undo(self : Self) -> None:
        self._scene.netlist.removeSegment(self._node1, self._node2)
        self._node1.onConnectionChange()
        self._node2.onConnectionChange()
        self._seg.setNode1(None)
        self._seg.setNode2(None)
        self._scene.removeItem(self._seg)

    def seg(self : Self) -> SegmentItem:
        return self._seg


class CmdRemoveSegment(CmdDiagramSceneBase):
    """
    Remove a specified segment from the scene.
    Updates both graphics and graph.
    Does not remove free nodes; the API layer may follow with
    CmdRemoveFreeNode for any orphaned free nodes.
    """

    # instance attributes
    _node1 : NodeItem
    _node2 : NodeItem
    _seg   : SegmentItem

    def __init__(
        self  : Self,
        scene : "DiagramScene",
        seg   : SegmentItem
    ) -> None:
        super().__init__(scene)
        self._node1 = seg.node1()
        self._node2 = seg.node2()
        self._seg = seg

    def redo(self : Self) -> None:
        self._scene.netlist.removeSegment(self._node1, self._node2)
        self._node1.onConnectionChange()
        self._node2.onConnectionChange()
        self._seg.setNode1(None)
        self._seg.setNode2(None)
        self._scene.removeItem(self._seg)

    def undo(self : Self) -> None:
        self._seg.setNode1(self._node1)
        self._seg.setNode2(self._node2)
        self._scene.addItem(self._seg)
        self._scene.netlist.addSegment(self._seg)
        self._node1.onConnectionChange()
        self._node2.onConnectionChange()


class CmdSplitSegment(CmdDiagramSceneBase):
    """Split a segment at a node. Updates both graphics and graph."""

    # instance attributes
    _node  : NodeItem     # node at split point
    _node1 : NodeItem     # original near node of seg1
    _node2 : NodeItem     # original far node of seg1
    _seg1  : SegmentItem  # existing segment (shortened to node1--node)
    _seg2  : SegmentItem  # new segment (node--node2)

    def __init__(
        self  : Self,
        scene : "DiagramScene",
        seg   : SegmentItem,
        node  : NodeItem
    ) -> None:
        super().__init__(scene)
        self._node = node
        self._node1 = seg.node1()
        self._node2 = seg.node2()
        self._seg1 = seg
        self._seg2 = SegmentItem()

    def redo(self : Self) -> None:
        # graph: drop the original edge while seg1 still has its old endpoints
        self._scene.netlist.removeSegment(self._node1, self._node2)
        # graphics: shorten seg1, create seg2 (so each segment knows its
        # endpoints before the corresponding addSegment(seg) call)
        self._seg1.setNode2(self._node)
        self._seg2.setNode1(self._node)
        self._seg2.setNode2(self._node2)
        self._scene.addItem(self._seg2)
        # graph: register the two new edges
        self._scene.netlist.addSegment(self._seg1)
        self._scene.netlist.addSegment(self._seg2)
        self._node.onConnectionChange()
        self._node1.onConnectionChange()
        self._node2.onConnectionChange()

    def undo(self : Self) -> None:
        # graph: drop both halves while seg1/seg2 still have their split endpoints
        self._scene.netlist.removeSegment(self._node1, self._node)
        self._scene.netlist.removeSegment(self._node, self._node2)
        # graphics: restore seg1, retire seg2
        self._seg1.setNode2(self._node2)
        self._seg2.setNode1(None)
        self._seg2.setNode2(None)
        self._scene.removeItem(self._seg2)
        # graph: re-register the original edge
        self._scene.netlist.addSegment(self._seg1)
        self._node.onConnectionChange()
        self._node1.onConnectionChange()
        self._node2.onConnectionChange()


class CmdUnsplitSegment(CmdDiagramSceneBase):
    """
    Unsplit a segment at a specified free node. Updates both graphics and
    graph. Assumption: free node has exactly 2 graph edges.
    """

    # instance attributes
    _node : FreeNodeItem  # free node being removed
    _far1 : NodeItem      # far node of seg1
    _far2 : NodeItem      # far node of seg2
    _seg1 : SegmentItem   # surviving segment (far1--far2 after redo)
    _seg2 : SegmentItem   # removed segment

    def __init__(
        self  : Self,
        scene : "DiagramScene",
        node  : FreeNodeItem
    ) -> None:
        super().__init__(scene)
        self._node = node
        segs = node.segments()
        self._seg1 = segs[0]
        self._seg2 = segs[1]
        self._far1 = self._seg1.otherNode(node)
        self._far2 = self._seg2.otherNode(node)

    def redo(self : Self) -> None:
        # graph: drop both edges and the middle node while geometry is still split
        self._scene.netlist.removeSegment(self._far1, self._node)
        self._scene.netlist.removeSegment(self._node, self._far2)
        self._scene.netlist.removeNodes(self._node)
        # graphics: extend seg1 to span far1--far2, retire seg2 and middle node
        self._seg1.changeNode(self._node, self._far2)
        self._seg2.setNode1(None)
        self._seg2.setNode2(None)
        self._scene.removeItem(self._seg2)
        self._scene.removeItem(self._node)
        # graph: register the merged edge (seg1 now ends at far2)
        self._scene.netlist.addSegment(self._seg1)
        self._far1.onConnectionChange()
        self._far2.onConnectionChange()

    def undo(self : Self) -> None:
        # graph: drop the merged edge while seg1 still spans far1--far2
        self._scene.netlist.removeSegment(self._far1, self._far2)
        # graphics: re-insert middle node, shorten seg1 back, restore seg2
        self._scene.addItem(self._node)
        self._seg1.changeNode(self._far2, self._node)
        self._seg2.setNode1(self._node)
        self._seg2.setNode2(self._far2)
        self._scene.addItem(self._seg2)
        # graph: re-register the two split edges (addSegment re-adopts _node)
        self._scene.netlist.addSegment(self._seg1)
        self._scene.netlist.addSegment(self._seg2)
        self._far1.onConnectionChange()
        self._far2.onConnectionChange()
        self._node.onConnectionChange()


class CmdSplitNet(CmdDiagramSceneBase):
    """
    Split a net at the specified node pair.
    Assumption: the nodes are part of the same net.
    """

    # instance attributes
    _node1 : NodeItem
    _node2 : NodeItem
    _net1  : Net | None  # post-split net on node 1 (or None if no net)
    _net2  : Net | None  # post-split net on node 2 (or None if no net)

    def __init__(
        self  : Self,
        scene : "DiagramScene",
        node1 : NodeItem,
        node2 : NodeItem
    ) -> None:
        super().__init__(scene)
        self._node1 = node1
        self._node2 = node2

    def redo(self : Self) -> None:
        self._scene.netlist.removeSegment(self._node1, self._node2)
