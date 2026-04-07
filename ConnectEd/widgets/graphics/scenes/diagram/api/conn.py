from math        import isclose

from PyQt6.QtCore import Qt, QPointF, QLineF
from PyQt6.QtGui  import QPainterPath, QPainterPathStroker

from ....items.vertex  import VertexItem
from ....items.segment import SegmentItem

from ...drawing.cmd import cmdExec

from ..cmd.conn import CmdAddVertex, CmdAddSegment, \
                       CmdSplitSegment, CmdUnsplitSegment

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
        Split any crossing segment(s) and join their net(s).
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

    def getVertex(
        self     : "DiagramScene",
        pos      : QPointF,         # scene coordinates
        undoable : bool = False
    ) -> VertexItem:
        """Get a vertex if present, add if necessary."""
        items = self.items(pos)
        for item in items:
            if isinstance(item, VertexItem):
                return item
        return self.addVertex(pos, undoable)

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
        p1 = seg1.otherVtx(vtx).scenePos()
        p2 = seg2.otherVtx(vtx).scenePos()
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
        v1 = self.getVertex(p1, undoable)
        v2 = self.getVertex(p2, undoable)
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
            if self._graph.has_edge(v1, v2):
                continue
            # add segment
            cmd = CmdAddSegment(self, v1, v2)
            cmdExec(self, cmd, undoable)
            self._graph.add_edge(v1, v2, segment=cmd.seg())
        # check if last vertex is redundant and remove if so
        if self.isRedundantVertex(v2):
            self.delVertex(v2, undoable)
        # end macro
        if undoable:
            self.undo_stack.endMacro()
