from __future__ import annotations

from typing import Self

from math   import isclose

from PyQt6.QtCore import Qt, QPointF, QLineF
from PyQt6.QtGui  import QPainterPath, QPainterPathStroker

from ......core.check import checked

from ....items.node      import NodeItem, FreeNodeItem, FixedNodeItem
from ....items.segment   import SegmentItem

from ..cmd import cmdExec

from ..cmd.conn import (
    CmdAddFreeNode, CmdRemoveFreeNode,
    CmdReplaceSegmentNode, CmdDetachSegmentNode,
    CmdAddSegment, CmdRemoveSegment,
    CmdSplitSegment, CmdUnsplitSegment
)

from ..host import asDiagramScene


class DiagramSceneApiConnMixin:
    """Connectivity API."""

    @checked
    def addFreeNode(
        self     : Self,
        pos      : QPointF,
        undoable : bool = False
    ) -> FreeNodeItem:
        """
        Add a free node to the scene (graphics only until wired).
        Split any crossing segment(s) and merge their net(s).
        """
        # create free node
        host = asDiagramScene(self)
        cmd = CmdAddFreeNode(host, pos)
        cmdExec(host, cmd, undoable)
        node = cmd.node()
        # split crossing segments at new node, joining nets as required
        items = host.items(pos)
        for seg in [item for item in items if isinstance(item, SegmentItem)]:
            cmdExec(host, CmdSplitSegment(host, seg, node), undoable)
        # done
        return node

    @checked
    def removeFreeNode(
        self     : Self,
        node     : FreeNodeItem,
        undoable : bool = False
    ) -> None:
        """Remove an orphan free node from the scene (graphics only)."""
        host = asDiagramScene(self)
        cmd = CmdRemoveFreeNode(host, node)
        cmdExec(host, cmd, undoable)

    @checked
    def replaceSegmentNode(
        self     : Self,
        segment  : SegmentItem,
        node_old : NodeItem,
        node_new : NodeItem,
        undoable : bool = False
    ) -> None:
        """
        Replace one node with another. Typically used for free/non swaps.
        """
        host = asDiagramScene(self)
        cmd = CmdReplaceSegmentNode(host, segment, node_old, node_new)
        cmdExec(host, cmd, undoable)

    @checked
    def detachSegmentNode(
        self     : Self,
        segment  : SegmentItem,
        node     : FixedNodeItem,
        undoable : bool = False
    ) -> FreeNodeItem:
        """Detach segment from fixed node, connect to new free node."""
        host = asDiagramScene(self)
        cmd = CmdDetachSegmentNode(host, segment, node)
        cmdExec(host, cmd, undoable)
        return cmd.freeNode()

    @checked
    def detachFixedNode(
        self     : Self,
        node     : FixedNodeItem,
        undoable : bool = False
    ) -> list[FreeNodeItem]:
        """Detach every segment from a fixed node."""
        host = asDiagramScene(self)
        free_nodes : list[FreeNodeItem] = []
        for segment in list(node.segments()):
            free_nodes.append(
                host.detachSegmentNode(segment, node, undoable)
            )
        return free_nodes

    @checked
    def getNode(
        self     : Self,
        pos      : QPointF,         # scene coordinates
        undoable : bool = False
    ) -> NodeItem:
        """
        Get a node if present, add a free node if necessary.
        Useful for adding segments.
        """
        host = asDiagramScene(self)
        items = host.items(pos)
        for item in items:
            if isinstance(item, NodeItem):
                return item
        return host.addFreeNode(pos, undoable)

    @checked
    def isRedundantNode(self : Self, node : NodeItem) -> bool:
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
        other1 = seg1.otherNode(node)
        other2 = seg2.otherNode(node)
        if other1 is None or other2 is None:
            return False
        p1 = other1.scenePos()
        p2 = other2.scenePos()
        uv1 = QLineF(node.scenePos(), p1).unitVector()
        uv2 = QLineF(node.scenePos(), p2).unitVector()
        dot_product = uv1.dx() * uv2.dx() + uv1.dy() * uv2.dy()
        return isclose(dot_product, -1.0, abs_tol=1e-6)

    @checked
    def connectFixedNode(
        self     : Self,
        node     : FixedNodeItem,
        undoable : bool = False
    ) -> None:
        """
        Connect a (unconnected) fixed node, e.g. after place/paste/clone/move.
        """
        host = asDiagramScene(self)
        if node.degree() > 0:
            return
        # get items at node position
        items = host.items(node.scenePos())
        nodes = [item for item in items if isinstance(item, NodeItem)]
        # merge coincident free nodes into this fixed node
        free_nodes = [n for n in nodes if isinstance(n, FreeNodeItem)]
        for free_node in free_nodes:
            for free_segment in list(free_node.segments()):
                host.replaceSegmentNode(free_segment, free_node, node, undoable)
            if free_node.scene() is not None and free_node.degree() == 0:
                host.removeFreeNode(free_node, undoable)
        # add zero length segments between this and other fixed nodes if required
        fixed_nodes = [
            fixed_node for fixed_node in nodes
            if isinstance(fixed_node, FixedNodeItem)
            and fixed_node != node
        ]
        for fixed_node in fixed_nodes:
            if not host.netlist.hasSegment(node, fixed_node):
                host.addSegment(node.scenePos(), fixed_node.scenePos(), undoable)
        # split crossing segments
        crossing_segments = [
            item for item in items
            if isinstance(item, SegmentItem)
            and item.node1() not in nodes
            and item.node2() not in nodes
        ]
        for segment in crossing_segments:
            cmdExec(host, CmdSplitSegment(host, segment, node), undoable)

    @checked
    def connectFixedNodes(
        self     : Self,
        nodes    : list[FixedNodeItem],
        undoable : bool = False
    ) -> None:
        """Connect a list of fixed nodes."""
        host = asDiagramScene(self)
        for node in nodes:
            host.connectFixedNode(node, undoable)

    @checked
    def addSegment(
        self        : Self,
        p1_or_node1 : QPointF | NodeItem,
        p2_or_node2 : QPointF | NodeItem,
        undoable    : bool = False
    ) -> None:
        """
        Create or find node at each endpoint.
        """
        host = asDiagramScene(self)
        # get/create endpoint vertices/entries
        if isinstance(p1_or_node1, QPointF):
            p1 = p1_or_node1
            node1 = host.getNode(p1_or_node1, undoable)
        else:
            node1 = p1_or_node1
            p1 = node1.scenePos()
        if isinstance(p2_or_node2, QPointF):
            p2 = p2_or_node2
            node2 = host.getNode(p2_or_node2, undoable)
        else:
            node2 = p2_or_node2
            p2 = node2.scenePos()
        # special case: zero length segment
        if p1 == p2 and node1 != node2:
            cmdExec(host, CmdAddSegment(host, node1, node2), undoable)
            return
        # begin macro
        if undoable:
            host.undo_stack.beginMacro("addSegment")
        # get vertices items along line from p1 to p2
        line_path = QPainterPath()
        line_path.moveTo(p1)
        line_path.lineTo(p2)
        stroker = QPainterPathStroker()
        stroker.setWidth(1.0)  # hit tolerance in scene units
        stroker.setCapStyle(Qt.PenCapStyle.FlatCap)  # don't extend beyond endpoints
        stroker_path = stroker.createStroke(line_path)
        nodes = [
            item for item in host.items(stroker_path) \
                if isinstance(item, NodeItem)
        ]
        # sort by distance from p1
        nodes.sort(key=lambda v: QLineF(p1, v.scenePos()).length())
        # add segments between all consecutive pairs of vertices
        for node1, node2 in zip(nodes[:-1], nodes[1:], strict=True):
            if host.netlist.hasSegment(node1, node2):
                continue
            cmdExec(host, CmdAddSegment(host, node1, node2), undoable)
        # cull redundant nodes (free, childless, degree 2, colinear neighbours).
        # Sweeping post-add catches both endpoints and any intermediate vertex
        # picked up by the stroker hit-test.
        for node in nodes:
            if isinstance(node, FreeNodeItem) and host.isRedundantNode(node):
                cmdExec(host, CmdUnsplitSegment(host, node), undoable)
        # end macro
        if undoable:
            host.undo_stack.endMacro()

    @checked
    def removeSegment(
        self     : Self,
        seg      : SegmentItem,
        undoable : bool = False,
    ) -> None:
        """Remove a segment, cull orphan free nodes."""
        host = asDiagramScene(self)
        cmdExec(host, CmdRemoveSegment(host, seg), undoable)
