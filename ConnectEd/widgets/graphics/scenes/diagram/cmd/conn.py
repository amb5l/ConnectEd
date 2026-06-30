from __future__ import annotations

from typing import Self

from PyQt6.QtCore import QPointF

from ......app import logger

from ......core.check import checked

from ....items.node    import NodeItem, FreeNodeItem
from ....items.segment import SegmentItem

from ..cmd import CmdSceneBase

from ..netlist import Net

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DiagramScene


class CmdDiagramSceneBase(CmdSceneBase):
    # instance attributes
    _scene : DiagramScene

    @checked
    def __init__(self : Self, scene : DiagramScene) -> None:
        super().__init__(scene)


class CmdAddFreeNode(CmdDiagramSceneBase):
    """
    Create and add a new free node to the scene (graphics only).
    The netlist adopts the node when the first segment is added.
    """

    # instance attributes
    _node : FreeNodeItem

    @checked
    def __init__(
        self  : Self,
        scene : DiagramScene,
        pos   : QPointF
    ) -> None:
        super().__init__(scene)
        self._node = FreeNodeItem(pos)

    @checked
    def redo(self : Self) -> None:
        self._scene.addItem(self._node)

    @checked
    def undo(self : Self) -> None:
        self._scene.removeItem(self._node)

    @checked
    def node(self : Self) -> FreeNodeItem:
        return self._node


class CmdRemoveFreeNode(CmdDiagramSceneBase):
    """Remove an orphan free node from the scene (graphics only)."""

    _node : FreeNodeItem

    @checked
    def __init__(
        self  : Self,
        scene : DiagramScene,
        node  : FreeNodeItem
    ) -> None:
        super().__init__(scene)
        self._node = node

    @checked
    def redo(self : Self) -> None:
        self._scene.removeItem(self._node)

    @checked
    def undo(self : Self) -> None:
        self._scene.addItem(self._node)


class CmdReplaceSegmentNode(CmdDiagramSceneBase):
    """
    Replace one node with another. Typically used for free/non swaps.
    Updates both graphics and graph.
    """

    _segment : SegmentItem
    _node_old : NodeItem
    _node_new : NodeItem

    @checked
    def __init__(
        self    : Self,
        scene     : DiagramScene,
        segment   : SegmentItem,
        node_old  : NodeItem,
        node_new  : NodeItem
    ) -> None:
        super().__init__(scene)
        self._segment = segment
        self._node_old = node_old
        self._node_new = node_new

    @checked
    def redo(self : Self) -> None:
        self._scene.netlist.replaceSegmentNode(
            self._segment, self._node_old, self._node_new
        )
        self._node_old.onConnectionChanged()
        self._node_new.onConnectionChanged()

    @checked
    def undo(self : Self) -> None:
        self._scene.netlist.replaceSegmentNode(
            self._segment, self._node_new, self._node_old
        )
        self._node_old.onConnectionChanged()
        self._node_new.onConnectionChanged()


class CmdDetachSegmentNode(CmdDiagramSceneBase):
    """
    Detach a segment from a fixed node, leaving a free node at the old attach
    point. Updates both graphics and graph.
    """

    _segment    : SegmentItem
    _node_fixed : NodeItem
    _node_free  : FreeNodeItem

    @checked
    def __init__(
        self    : Self,
        scene   : DiagramScene,
        segment : SegmentItem,
        node    : NodeItem,
    ) -> None:
        super().__init__(scene)
        self._segment    = segment
        self._node_fixed = node
        self._node_free  = FreeNodeItem(node.scenePos())

    @checked
    def redo(self : Self) -> None:
        self._scene.addItem(self._node_free)
        self._scene.netlist.replaceSegmentNode(
            self._segment, self._node_fixed, self._node_free
        )
        self._node_fixed.onConnectionChanged()
        self._node_free.onConnectionChanged()

    @checked
    def undo(self : Self) -> None:
        self._scene.netlist.replaceSegmentNode(
            self._segment, self._node_free, self._node_fixed
        )
        self._scene.removeItem(self._node_free)
        self._node_fixed.onConnectionChanged()

    @checked
    def freeNode(self : Self) -> FreeNodeItem:
        return self._node_free


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

    @checked
    def __init__(
        self  : Self,
        scene : DiagramScene,
        node1 : NodeItem,
        node2 : NodeItem
    ) -> None:
        super().__init__(scene)
        self._node1 = node1
        self._node2 = node2
        self._seg = SegmentItem()

    @checked
    def redo(self : Self) -> None:
        self._seg.setNode1(self._node1)
        self._seg.setNode2(self._node2)
        self._scene.addItem(self._seg)
        self._scene.netlist.addSegment(self._seg)
        self._node1.onConnectionChanged()
        self._node2.onConnectionChanged()

    @checked
    def undo(self : Self) -> None:
        self._scene.netlist.removeSegment(self._node1, self._node2)
        self._node1.onConnectionChanged()
        self._node2.onConnectionChanged()
        self._seg.setNode1(None)
        self._seg.setNode2(None)
        self._scene.removeItem(self._seg)

    @checked
    def seg(self : Self) -> SegmentItem:
        return self._seg


class CmdRemoveSegment(CmdDiagramSceneBase):
    """
    Remove a segment from the scene and netlist. Cull orphan free nodes.
    """

    # instance attributes
    _node1  : NodeItem
    _node2  : NodeItem
    _seg    : SegmentItem
    _culled : list[FreeNodeItem]

    @checked
    def __init__(
        self  : Self,
        scene : DiagramScene,
        seg   : SegmentItem
    ) -> None:
        super().__init__(scene)
        node1 = seg.node1()
        node2 = seg.node2()
        if node1 is None or node2 is None:
            logger().error("Missing nodes")
            self.setObsolete(True)
            return
        self._node1  = node1
        self._node2  = node2
        self._seg    = seg
        self._culled = []

    @checked
    def redo(self : Self) -> None:
        self._scene.netlist.removeSegment(self._node1, self._node2)
        self._node1.onConnectionChanged()
        self._node2.onConnectionChanged()
        self._seg.setNode1(None)
        self._seg.setNode2(None)
        self._scene.removeItem(self._seg)
        self._culled = []
        for node in (self._node1, self._node2):
            if not isinstance(node, FreeNodeItem):
                continue
            if node.degree() > 0:
                continue
            if node.scene() is None:
                continue
            if self._scene.netlist.hasNode(node):
                self._scene.netlist.removeNodes(node)
            self._scene.removeItem(node)
            self._culled.append(node)

    @checked
    def undo(self : Self) -> None:
        for node in self._culled:
            self._scene.addItem(node)
            node.onConnectionChanged()
        self._seg.setNode1(self._node1)
        self._seg.setNode2(self._node2)
        self._scene.addItem(self._seg)
        self._scene.netlist.addSegment(self._seg)
        self._node1.onConnectionChanged()
        self._node2.onConnectionChanged()


class CmdSplitSegment(CmdDiagramSceneBase):
    """Split a segment at a node. Updates both graphics and graph."""

    # instance attributes
    _node  : NodeItem     # node at split point
    _node1 : NodeItem     # original near node of seg1
    _node2 : NodeItem     # original far node of seg1
    _seg1  : SegmentItem  # existing segment (shortened to node1--node)
    _seg2  : SegmentItem  # new segment (node--node2)

    @checked
    def __init__(
        self  : Self,
        scene : DiagramScene,
        seg   : SegmentItem,
        node  : NodeItem
    ) -> None:
        super().__init__(scene)
        self._node = node
        node1 = seg.node1()
        node2 = seg.node2()
        if node1 is None or node2 is None:
            logger().error("Missing nodes")
            self.setObsolete(True)
            return
        self._node1 = node1
        self._node2 = node2
        self._seg1 = seg
        self._seg2 = SegmentItem()

    @checked
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
        self._node.onConnectionChanged()
        self._node1.onConnectionChanged()
        self._node2.onConnectionChanged()

    @checked
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
        self._node.onConnectionChanged()
        self._node1.onConnectionChanged()
        self._node2.onConnectionChanged()


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

    @checked
    def __init__(
        self  : Self,
        scene : DiagramScene,
        node  : FreeNodeItem
    ) -> None:
        super().__init__(scene)
        self._node = node
        segs = node.segments()
        self._seg1 = segs[0]
        self._seg2 = segs[1]
        far1 = self._seg1.otherNode(node)
        far2 = self._seg2.otherNode(node)
        if far1 is None or far2 is None:
            logger().error("Missing far nodes")
            self.setObsolete(True)
            return
        self._far1 = far1
        self._far2 = far2

    @checked
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
        self._far1.onConnectionChanged()
        self._far2.onConnectionChanged()

    @checked
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
        self._far1.onConnectionChanged()
        self._far2.onConnectionChanged()
        self._node.onConnectionChanged()


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

    @checked
    def __init__(
        self  : Self,
        scene : DiagramScene,
        node1 : NodeItem,
        node2 : NodeItem
    ) -> None:
        super().__init__(scene)
        self._node1 = node1
        self._node2 = node2

    @checked
    def redo(self : Self) -> None:
        self._scene.netlist.removeSegment(self._node1, self._node2)
