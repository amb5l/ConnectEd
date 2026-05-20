from math        import isclose

from PyQt6.QtCore import Qt, QPointF, QLineF
from PyQt6.QtGui  import QPainterPath, QPainterPathStroker

from ......app import logger

from ......core.check import checked

from ....items.node      import NodeItem, FreeNodeItem, FixedNodeItem, \
                                PinNodeItem, TapNodeItem
from ....items.segment   import SegmentItem
from ....items.net_label import NetLabelItem

from ...drawing.cmd import cmdExec, CmdDelete

from ..cmd.conn import CmdAddFreeNode, CmdReplaceNode, \
                       CmdAddSegment, CmdSplitSegment, CmdUnsplitSegment, \
                       CmdSplitNet

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
        Add a free node to the scene.
        Split any crossing segment(s) and merge their net(s).
        Assumption: no existing nodes at this point.
        """
        # create free node
        cmd = CmdAddFreeNode(self, pos)
        cmdExec(self, cmd, undoable)
        node = cmd.node()
        # split crossing segments at new node, joining nets as required
        items = self.items(pos)
        for seg in [item for item in items if isinstance(item, SegmentItem)]:
            cmd = CmdSplitSegment(self, seg, node)
            cmdExec(self, cmd, undoable)
        # done
        return node

    @checked
    def removeFreeNode(
        self     : "DiagramScene",
        node     : FreeNodeItem,
        undoable : bool = False
    ) -> None:
        """
        Remove a free node from the scene.
        Unsplit any crossing segments.
        If label(s) are attached, they go with it.
        """
        cmd = CmdDelete(self, [node])
        cmdExec(self, cmd, undoable)

    @checked
    def replaceNode(
        self     : "DiagramScene",
        node1    : NodeItem,
        node2    : NodeItem,
        undoable : bool = False
    ) -> None:
        """
        Replace one node with another. Typically used for free/non swaps.
        """
        cmd = CmdReplaceNode(self, node1, node2)
        cmdExec(self, cmd, undoable)

    @checked
    def getNode(
        self     : "DiagramScene",
        pos      : QPointF,         # scene coordinates
        undoable : bool = False
    ) -> NodeItem:
        """
        Get a node if present, add a free node if necessary.
        Useful for adding segments, placing labels etc.
        """
        items = self.items(pos)
        for item in items:
            if isinstance(item, NodeItem):
                return item
        return self.addFreeNode(pos, undoable)

    @checked
    def detachNode(
        self     : "DiagramScene",
        node     : FixedNodeItem,
        undoable : bool = False
    ) -> None:
        """
        Detach a node from existing connectivity.
        Used in move (not slide) interaction for nodes touching nodes
        that will not move nodes on unselected items, and unselected
        segment endpoints (for which a replacement node will be added).
        Remove orphan zero length segments.
        Melt redundant segment splits.
        """
        cmd = CmdDetachNode(self, node)
        cmdExec(self, cmd, undoable)

    @checked
    def detachSegment(
        self     : "DiagramScene",
        seg      : SegmentItem,
        node     : NodeItem,
        undoable : bool = False
    ) -> None:
        """
        Lift a segment node away from existing connectivity.
        Used in move (not slide) interaction for segments touching nodes
        that will not move e.g. pins on unselected blocks, vertices on
        unselected segments.
        If attached to a pin or tap node, add a new free node at the segment
        endpoint and leave the pin or tap node behind.
        If attached to a free node needed for other segments, ditto.
        Melt redundant segment splits.
        """

    @checked
    def dropSegmentNode(
        self     : "DiagramScene",
        seg      : SegmentItem,
        node     : FreeNodeItem,
        undoable : bool = False
    ) -> None:
        """
        Drop a segment node back into the scene.
        Replace node with an existing node if present.
        """

    @checked
    def addNode(
        self     : "DiagramScene",
        node     : PinNodeItem | TapNodeItem,
        undoable : bool = False
    ) -> PinNodeItem | TapNodeItem:
        """
        Process the addition of a node to the scene, e.g. as the result
        of a move, paste/duplicate or place operation.
        """
        cmd = CmdAddNode(self, node)
        cmdExec(self, cmd, undoable)
        return cmd.node()

    @checked
    def isRedundantNode(self : "DiagramScene", node : NodeItem) -> bool:
        """
        Node is redundant if
        - free
        - parentless (should always be true for free nodes)
        - childless (not parenting a property text)
        - breaks up a straight line.
        """
        if not isinstance(node, FreeNodeItem) \
        or node.parentItem() is not None \
        or len(node.childItems()) != 0 \
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
    def addSegment(
        self     : "DiagramScene",
        p1       : QPointF,
        p2       : QPointF,
        undoable : bool = False
    ) -> None:
        """
        Create or find node at each endpoint.

        """
        # handle zero length - can happen on double click
        if p1 == p2:
            return  # do nothing
        # begin macro
        if undoable:
            self.undo_stack.beginMacro("addSegment")
        # get/create endpoint vertices/entries
        v1 = self.getNode(p1, undoable)
        v2 = self.getNode(p2, undoable)
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
        for v1, v2 in zip(nodes[:-1], nodes[1:], strict=True):
            if self.netlist.hasSegment(v1, v2):
                continue
            cmd = CmdAddSegment(self, v1, v2)
            cmdExec(self, cmd, undoable)
        # cull redundant nodes (free, childless, degree 2, colinear neighbours).
        # Sweeping post-add catches both endpoints and any intermediate vertex
        # picked up by the stroker hit-test.
        for node in nodes:
            if self.isRedundantNode(node):
                cmd = CmdUnsplitSegment(self, node)
                cmdExec(self, cmd, undoable)
        # end macro
        if undoable:
            self.undo_stack.endMacro()

    @checked
    def removeSegment(
        self     : "DiagramScene",
        seg      : SegmentItem,
        undoable : bool = False
    ) -> None:
        """
        Remove a segment from the scene.
        Remove any orphan free vertices.
        """
        # begin macro
        if undoable:
            self.undo_stack.beginMacro("removeSegment")
        # remove segment
        node1 = seg.node1()
        node2 = seg.node2()
        cmd = CmdDelete(self, [seg])
        cmdExec(self, cmd, undoable)
        # split net
        cmd = CmdSplitNet(self, node1, node2)
        cmdExec(self, cmd, undoable)
        # remove labels and orphan free vertices
        for node in [node1, node2]:
            if not isinstance(node, FreeNodeItem):
                continue  # not a free node
            if node.parentItem() is not None:
                logger().warning(f"FreeNode {node} has a parent")
                continue  # free node with parent???
            if node.degree() > 0:
                continue  # is connected to other segments so not an orphan
            # orderly removal of labels
            for child in node.childItems():
                if isinstance(child, NetLabelItem):
                    cmd = CmdDelete(self, [child])
                    cmdExec(self, cmd, undoable)
            if node.childItems() != []:
                continue  # is parenting a label so not an orphan
            cmd = CmdDelete(self, [node])
            cmdExec(self, cmd, undoable)
        # end macro
        if undoable:
            self.undo_stack.endMacro()
