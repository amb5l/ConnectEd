from math        import isclose

from PyQt6.QtCore import Qt, QPointF, QLineF
from PyQt6.QtGui  import QPainterPath, QPainterPathStroker

from ......core.check import checked

from ....items.node      import NodeItem, FreeNodeItem, FixedNodeItem
from ....items.segment   import SegmentItem

from ...drawing.cmd import cmdExec

from ..cmd.conn import CmdAddFreeNode, CmdRemoveFreeNode, \
                       CmdReplaceSegmentNode, CmdDetachSegmentNode, \
                       CmdAddSegment, CmdRemoveSegment, \
                       CmdSplitSegment, CmdUnsplitSegment

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DiagramScene


class DiagramSceneApiConnMixin:
    """Connectivity API."""

    @checked
    def addFreeNode(
        self     : "DiagramScene",
        pos      : QPointF,
        undoable : bool = False
    ) -> FreeNodeItem:
        """
        Add a free node to the scene (graphics only until wired).
        Split any crossing segment(s) and merge their net(s).
        """
        # create free node
        cmd = CmdAddFreeNode(self, pos)
        cmdExec(self, cmd, undoable)
        node = cmd.node()
        # split crossing segments at new node, joining nets as required
        items = self.items(pos)
        for seg in [item for item in items if isinstance(item, SegmentItem)]:
            cmdExec(self, CmdSplitSegment(self, seg, node), undoable)
        # done
        return node

    @checked
    def removeFreeNode(
        self     : "DiagramScene",
        node     : FreeNodeItem,
        undoable : bool = False
    ) -> None:
        """Remove an orphan free node from the scene (graphics only)."""
        cmd = CmdRemoveFreeNode(self, node)
        cmdExec(self, cmd, undoable)

    @checked
    def replaceSegmentNode(
        self     : "DiagramScene",
        segment  : SegmentItem,
        node_old : NodeItem,
        node_new : NodeItem,
        undoable : bool = False
    ) -> None:
        """
        Replace one node with another. Typically used for free/non swaps.
        """
        cmd = CmdReplaceSegmentNode(self, segment, node_old, node_new)
        cmdExec(self, cmd, undoable)

    @checked
    def detachSegmentNode(
        self     : "DiagramScene",
        segment  : SegmentItem,
        node     : FixedNodeItem,
        undoable : bool = False
    ) -> FreeNodeItem:
        """Detach segment from fixed node, connect to new free node."""
        cmd = CmdDetachSegmentNode(self, segment, node)
        cmdExec(self, cmd, undoable)
        return cmd.freeNode()

    @checked
    def detachFixedNode(
        self     : "DiagramScene",
        node     : FixedNodeItem,
        undoable : bool = False
    ) -> list[FreeNodeItem]:
        """Detach every segment from a fixed node."""
        free_nodes : list[FreeNodeItem] = []
        for segment in list(node.segments()):
            free_nodes.append(
                self.detachSegmentNode(segment, node, undoable)
            )
        return free_nodes

    @checked
    def getNode(
        self     : "DiagramScene",
        pos      : QPointF,         # scene coordinates
        undoable : bool = False
    ) -> NodeItem:
        """
        Get a node if present, add a free node if necessary.
        Useful for adding segments.
        """
        items = self.items(pos)
        for item in items:
            if isinstance(item, NodeItem):
                return item
        return self.addFreeNode(pos, undoable)

    @checked
    def isRedundantNode(self : "DiagramScene", node : NodeItem) -> bool:
        """
        Node is redundant if
        - free
        - parentless (should always be true for free nodes)
        - breaks up a straight line.
        """
        if not isinstance(node, FreeNodeItem) \
        or node.parentItem() is not None \
        or node.degree() != 2:
            return False
        seg1 = node.segments()[0]
        seg2 = node.segments()[1]
        p1 = seg1.otherNode(node).scenePos()
        p2 = seg2.otherNode(node).scenePos()
        uv1 = QLineF(node.scenePos(), p1).unitVector()
        uv2 = QLineF(node.scenePos(), p2).unitVector()
        dot_product = uv1.dx() * uv2.dx() + uv1.dy() * uv2.dy()
        return isclose(dot_product, -1.0, abs_tol=1e-6)

    @checked
    def connectFixedNode(
        self     : "DiagramScene",
        node     : FixedNodeItem,
        undoable : bool = False
    ) -> None:
        """
        Connect a (unconnected) fixed node, e.g. after place/paste/clone/move.
        """
        if node.degree() > 0:
            return
        # get items at node position
        items = self.items(node.scenePos())
        nodes = [item for item in items if isinstance(item, NodeItem)]
        # merge coincident free nodes into this fixed node
        free_nodes = [n for n in nodes if isinstance(n, FreeNodeItem)]
        for free_node in free_nodes:
            for free_segment in list(free_node.segments()):
                self.replaceSegmentNode(free_segment, free_node, node, undoable)
            if free_node.scene() is not None and free_node.degree() == 0:
                self.removeFreeNode(free_node, undoable)
        # add zero length segments between this and other fixed nodes if required
        fixed_nodes = [
            fixed_node for fixed_node in nodes
            if isinstance(fixed_node, FixedNodeItem)
            and fixed_node != node
        ]
        for fixed_node in fixed_nodes:
            if not self.netlist.hasSegment(node, fixed_node):
                self.addSegment(node.scenePos(), fixed_node.scenePos(), undoable)
        # split crossing segments
        crossing_segments = [
            item for item in items
            if isinstance(item, SegmentItem)
            and item.node1() not in nodes
            and item.node2() not in nodes
        ]
        for segment in crossing_segments:
            cmdExec(self, CmdSplitSegment(self, segment, node), undoable)

    @checked
    def connectFixedNodes(
        self     : "DiagramScene",
        nodes    : list[FixedNodeItem],
        undoable : bool = False
    ) -> None:
        """Connect a list of fixed nodes."""
        for node in nodes:
            self.connectFixedNode(node, undoable)

    @checked
    def addSegment(
        self        : "DiagramScene",
        p1_or_node1 : QPointF | NodeItem,
        p2_or_node2 : QPointF | NodeItem,
        undoable    : bool = False
    ) -> None:
        """
        Create or find node at each endpoint.
        """
        # get/create endpoint vertices/entries
        if isinstance(p1_or_node1, QPointF):
            p1 = p1_or_node1
            node1 = self.getNode(p1_or_node1, undoable)
        else:
            node1 = p1_or_node1
            p1 = node1.scenePos()
        if isinstance(p2_or_node2, QPointF):
            p2 = p2_or_node2
            node2 = self.getNode(p2_or_node2, undoable)
        else:
            node2 = p2_or_node2
            p2 = node2.scenePos()
        # special case: zero length segment
        if p1 == p2 and node1 != node2:
            cmdExec(self, CmdAddSegment(self, node1, node2), undoable)
            return
        # begin macro
        if undoable:
            self.undo_stack.beginMacro("addSegment")
        # get vertices items along line from p1 to p2
        line_path = QPainterPath()
        line_path.moveTo(p1)
        line_path.lineTo(p2)
        stroker = QPainterPathStroker()
        stroker.setWidth(1.0)  # hit tolerance in scene units
        stroker.setCapStyle(Qt.PenCapStyle.FlatCap)  # don't extend beyond endpoints
        stroker_path = stroker.createStroke(line_path)
        nodes = [
            item for item in self.items(stroker_path) \
                if isinstance(item, NodeItem)
        ]
        # sort by distance from p1
        nodes.sort(key=lambda v: QLineF(p1, v.scenePos()).length())
        # add segments between all consecutive pairs of vertices
        for node1, node2 in zip(nodes[:-1], nodes[1:], strict=True):
            if self.netlist.hasSegment(node1, node2):
                continue
            cmdExec(self, CmdAddSegment(self, node1, node2), undoable)
        # cull redundant nodes (free, childless, degree 2, colinear neighbours).
        # Sweeping post-add catches both endpoints and any intermediate vertex
        # picked up by the stroker hit-test.
        for node in nodes:
            if self.isRedundantNode(node):
                cmdExec(self, CmdUnsplitSegment(self, node), undoable)
        # end macro
        if undoable:
            self.undo_stack.endMacro()

    @checked
    def removeSegment(
        self     : "DiagramScene",
        seg      : SegmentItem,
        undoable : bool = False,
    ) -> None:
        """Remove a segment, cull orphan free nodes."""
        cmdExec(self, CmdRemoveSegment(self, seg), undoable)
