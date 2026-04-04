from typing      import Self
from collections import defaultdict
from math        import isclose

from PyQt6.QtCore import Qt, QPointF, QLineF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtGui  import QPainterPath, QPainterPathStroker

from ......app import logger

from ......core.types import Counter, DataKind
from ......core.xml   import toXmlAttrs
from ......core.utils import underscore2space

from ....properties import PropertiesMixin, InherentProperty

from ....items.vertex  import VertexItem, EntryItem
from ....items.segment import SegmentItem

from ..cmd      import cmdExec
from ..cmd.conn import CmdAddVertex,      \
                       CmdRemoveVertex,   \
                       CmdAddSegment,      \
                       CmdReattachSegment, \
                       CmdRemoveSegment,   \
                       CmdSplitSegment,    \
                       CmdUnsplitSegment,  \
                       CmdSplitNetEdge,    \
                       CmdUnsplitNetEdge

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


################################################################################
# local functions
################################################################################

def _xp(point : QPointF, line : QLineF) -> float:
    """Returns the cross product magnitude for colinearity (should be ~0)."""
    if line.isNull():  # degenerate line (zero length)
        return point == line.p1()
    h = point - line.p1()  # vector from p1 to point (AP)
    ab = line.p2() - line.p1()  # vector from p1 to p2 (AB)
    # cross product magnitude for collinearity (should be ~0)
    return h.x() * ab.y() - h.y() * ab.x()


def _pointOnInfiniteLine(
    point : QPointF,
    line  : QLineF,
    tol   : float = 1e-6
) -> bool:
    """Returns True if the point is on the infinite line."""
    cross_product = _xp(point, line)
    return isclose(cross_product, 0.0, abs_tol=tol)


def _colinear(line1 : QLineF, line2 : QLineF) -> bool:
    """
    Returns True if the lines are colinear.
    NOTE: they may or may not be touching or overlapping.
    """
    return \
        _pointOnInfiniteLine(line1.p1(), line2) and \
        _pointOnInfiniteLine(line1.p2(), line2) and \
        _pointOnInfiniteLine(line2.p1(), line1) and \
        _pointOnInfiniteLine(line2.p2(), line1)

################################################################################
# mixin
################################################################################

class DrawingSceneApiConnMixin:
    """Connectivity API."""

    def addVertex(
        self     : "DrawingScene",
        pos      : QPointF,
        undoable : bool = False
    ) -> VertexItem:
        """
        Add a vertex to the scene.
        Record it in ID:instance dict.
        Split any crossing segment(s) and join their net(s).
        """
        # create vertex
        cmd = CmdAddVertex(self, pos)
        cmdExec(self, cmd, undoable)
        vtx = cmd.vtx()
        # record vertex
        self._nodes[vtx._id] = vtx
        # split segments at new vertex, joining nets as required
        items = self.items(pos)
        for item in items:
            if not isinstance(item, SegmentItem):
                continue
            seg : SegmentItem = item
            net_edge = (seg.vtx1().id(), seg.vtx2().id())
            # mutate graphics
            cmd = CmdSplitSegment(self, seg, vtx)
            cmdExec(self, cmd, undoable)
            # mutate netlist
            cmd = CmdSplitNetEdge(self, net_edge, vtx.id())
            cmdExec(self, cmd, undoable)


            v1 : VertexItem = seg.vtx1()
            v2 : VertexItem = seg.vtx2()
            net = self.getNet(v1.netId())
            # connect new vertex net to segment net
            if vtx.netId() is None:
                # add new vertex to segment net
                cmd = CmdSplitNetEdge(self, (v1.id(), v2.id()), vtx.id())
                cmdExec(self, cmd, undoable)

            else:
                # join new vertex net to segment net
            # get near and far vertices
            l1 = QLineF(v1.scenePos(), pos).length()
            l2 = QLineF(v2.scenePos(), pos).length()
            v_near, v_far = v2, v1 if l2 < l1 else v1, v2
            # reconnect segment near vertex to new vertex
            cmd = CmdReattachSegment(self, seg, v_near, vtx)
            # create new segment from new
            # split net edge
            # create new segment from new to near vertex


            self.tidyVertex(vtx, undoable)
        return vtx

    def getVertex(
        self     : "DrawingScene",
        pos      : QPointF,         # scene coordinates
        undoable : bool = False
    ) -> VertexItem:
        """Get a vertex if present, add if necessary."""
        items = self.items(pos)
        for item in items:
            if isinstance(item, VertexItem):
                return item
        return self.addVertex(pos, undoable)

    def isRedundantVertex(self : "DrawingScene", vtx : VertexItem) -> bool:
        """
        Vertex is redundant if
        - it is parentless (not an entry)
        - it is childless (not parenting a property text)
        - it breaks up a straight line.
        """
        if vtx.parentItem() is not None \
        or len(vtx.childItems()) != 0 \
        or len(vtx.connections()) != 2:
            return False
        seg1 = vtx.connections()[0]
        seg2 = vtx.connections()[1]
        p1 = seg1.otherVtx(vtx).scenePos()
        p2 = seg2.otherVtx(vtx).scenePos()
        uv1 = QLineF(vtx.scenePos(), p1).unitVector()
        uv2 = QLineF(vtx.scenePos(), p2).unitVector()
        dot_product = uv1.dx() * uv2.dx() + uv1.dy() * uv2.dy()
        return isclose(dot_product, 1.0, abs_tol=1e-6)

    def getSegment(
        self : "DrawingScene",
        v1   : VertexItem,
        v2   : VertexItem
    ) -> SegmentItem | None:
        for seg in v1.connections():
            if seg.otherVtx(v1) == v2:
                return seg
        return None

    def addSegment(
        self     : "DrawingScene",
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
        for v1, v2 in zip(vertices[:-1], vertices[1:]):
            # check if v1 is redundant and remove if so
            if self.isRedundantVertex(v1):
                self.unsplitSegment(v1, undoable)
                continue
            # check for existing segment between v1 and v2
            if self.getSegment(v1, v2) is not None:
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

    def unsplitSegment(
        self     : "DrawingScene",
        vtx      : VertexItem,
        undoable : bool = False
    ) -> None:
        """Unsplit a segment at a specified vertex."""
        # graphics
        cmd = CmdUnsplitSegment(self, vtx)
        cmdExec(self, cmd, undoable)
        # netlist
        cmd = CmdUnsplitNetEdge(self, vtx.id())
        cmdExec(self, cmd, undoable)
