from math        import isclose

from PyQt6.QtCore import Qt, QPointF, QLineF
from PyQt6.QtGui  import QPainterPath, QPainterPathStroker

from ....items.node           import NodeItem
from ....items.vertex         import VertexItem
from ....items.entry          import EntryItem
from ....items.segment        import SegmentItem
from ....items.property_label import PropertyLabelItem

from ...drawing.cmd import cmdExec, CmdDelete

from ..cmd.conn import CmdAddVertex, \
                       CmdAddSegment, CmdSplitSegment, CmdUnsplitSegment, \
                       CmdSplitNet

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DiagramScene


class DiagramSceneApiConnMixin:
    """Connectivity API."""

    def addVertex(
        self     : "DiagramScene",
        pos      : QPointF,
        undoable : bool = False
    ) -> VertexItem:
        """
        Add a vertex to the scene.
        Split any crossing segment(s) and merge their net(s).
        Assumption: no existing vertices at this point.
        """
        # create vertex
        cmd = CmdAddVertex(self, pos)
        cmdExec(self, cmd, undoable)
        vtx = cmd.vtx()
        # split crossing segments at new vertex, joining nets as required
        items = self.items(pos)
        for seg in [item for item in items if isinstance(item, SegmentItem)]:
            cmd = CmdSplitSegment(self, seg, vtx)
            cmdExec(self, cmd, undoable)
        # done
        return vtx

    def removeVertex(
        self     : "DiagramScene",
        vtx      : VertexItem,
        undoable : bool = False
    ) -> None:
        """
        Remove a vertex from the scene.
        Unsplit any crossing segments.
        If label(s) are attached, they go with it.
        """
        cmd = CmdDelete(self, [vtx])
        cmdExec(self, cmd, undoable)

    def replaceNode(
        self     : "DiagramScene",
        node1    : NodeItem,
        node2    : NodeItem,
        undoable : bool = False
    ) -> None:
        """
        Replace one vertex with another. Typically used for entry/vertex swaps.
        """
        cmd = CmdReplaceNode(self, node1, node2)
        cmdExec(self, cmd, undoable)

    def getNode(
        self     : "DiagramScene",
        pos      : QPointF,         # scene coordinates
        undoable : bool = False
    ) -> VertexItem:
        """
        Get a node if present, add a vertex if necessary.
        Useful for adding segments, placing labels etc.
        """
        items = self.items(pos)
        for item in items:
            if isinstance(item, NodeItem):
                return item
        return self.addVertex(pos, undoable)

    def detachEntry(
        self : "DiagramScene",
        entry : EntryItem,
        undoable : bool = False
    ) -> None:
        """
        Detach an entry from existing connectivity.
        Used in move (not slide) interaction for entries touching nodes
        that will not move entries on unselected items, and unselected
        segment endpoints (for which a replacement vertex will be added).
        Remove orphan zero length segments.
        Melt redundant segment splits.
        """

    def detachSegment(
        self : "DiagramScene",
        seg  : SegmentItem,
        node : NodeItem,
        undoable : bool = False
    ) -> None:
        """
        Lift a segment node away from existing connectivity.
        Used in move (not slide) interaction for segments touching nodes
        that will not move e.g. pins on unselected blocks, vertices on
        unselected segments.
        If attached to an entry, add a new vertex at the segment endpoint and
        leave the entry behind.
        If attached to a vertex needed for other segments, ditto.
        Melt redundant segment splits.
        """

    def dropSegmentNode(
        self : "DiagramScene",
        seg  : SegmentItem,
        vtx  : VertexItem,
        undoable : bool = False
    ) -> None:
        """
        Drop a segment vertex back into the scene.
        Replace vertex with an existing entry if present.
        """


    def addEntry(
        self     : "DiagramScene",
        entry    : EntryItem,
        undoable : bool = False
    ) -> EntryItem:
        """
        Process the addition of an entry to the scene, e.g. as the result
        of a move, paste/duplicate or place operation.
        """
        cmd = CmdAddEntry(self, pos)
        cmdExec(self, cmd, undoable)
        return cmd.entry()


    def isRedundantVertex(self : "DiagramScene", vtx : VertexItem) -> bool:
        """
        Vertex is redundant if
        - it is parentless (not an entry)
        - it is childless (not parenting a property text)
        - it breaks up a straight line.
        """
        if vtx.parentItem() is not None \
        or len(vtx.childItems()) != 0 \
        or vtx.degree() != 2:
            return False
        seg1 = vtx.segments()[0]
        seg2 = vtx.segments()[1]
        p1 = seg1.otherNode(vtx).scenePos()
        p2 = seg2.otherNode(vtx).scenePos()
        uv1 = QLineF(vtx.scenePos(), p1).unitVector()
        uv2 = QLineF(vtx.scenePos(), p2).unitVector()
        dot_product = uv1.dx() * uv2.dx() + uv1.dy() * uv2.dy()
        return isclose(dot_product, 1.0, abs_tol=1e-6)

    def addSegment(
        self     : "DiagramScene",
        p1       : QPointF,
        p2       : QPointF,
        undoable : bool = False
    ) -> None:
        """
        Create or find vertex at each endpoint.

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
        vertices = [
            item for item in self.items(stroker_path) \
                if isinstance(item, VertexItem)
        ]
        # sort by distance from p1
        vertices.sort(key=lambda v: QLineF(p1, v.scenePos()).length())
        # add segments between all vertices along path from v1 to v2
        # iterate over all consecutive pairs of vertices
        for v1, v2 in zip(vertices[:-1], vertices[1:], strict=True):
            # check if v1 is redundant and remove if so
            if self.isRedundantVertex(v1):
                cmd = CmdUnsplitSegment(self, v1)
                cmdExec(self, cmd, undoable)
                continue
            # check for existing segment between v1 and v2
            if self.netlist.hasSegment(v1, v2):
                continue
            # add segment
            cmd = CmdAddSegment(self, v1, v2)
            cmdExec(self, cmd, undoable)
        # check if last vertex is redundant and remove if so
        if self.isRedundantVertex(v2):
            self.delVertex(v2, undoable)
        # end macro
        if undoable:
            self.undo_stack.endMacro()

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
        vtx1 = seg.node1()
        vtx2 = seg.node2()
        cmd = CmdDelete(self, [seg])
        cmdExec(self, cmd, undoable)
        # split net
        cmd = CmdSplitNet(self, vtx1, vtx2)
        cmdExec(self, cmd, undoable)
        # remove labels and orphan free vertices
        for vtx in [vtx1, vtx2]:
            if vtx.parentItem() is not None:
                continue  # is an entry so not a free vertex
            if vtx.degree() > 0:
                continue  # is connected to other segments so not an orphan
            # orderly removal of labels
            for child in vtx.childItems():
                if isinstance(child, PropertyLabelItem):
                    cmd = CmdDelete(self, [child])
                    cmdExec(self, cmd, undoable)
            if vtx.childItems() != []:
                continue  # is parenting a label so not an orphan
            cmd = CmdDelete(self, [vtx])
            cmdExec(self, cmd, undoable)
        # end macro
        if undoable:
            self.undo_stack.endMacro()
