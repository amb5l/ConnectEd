from math import isclose

from PyQt6.QtCore import QPointF, QLineF
from PyQt6.QtGui  import QPainterPath, QPainterPathStroker

from ......app import logger

from ......core.utils import itemsTypeDict

from ....items.vertex  import VertexItem
from ....items.segment import SegmentItem

from ..cmd      import cmdExec
from ..cmd.conn import CmdAddVertex,      \
                       CmdRemoveVertex,   \
                       CmdAddSegment,      \
                       CmdReattachSegment, \
                       CmdRemoveSegment

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
    """Connection handling."""

    def tidyVertex(self : "DrawingScene", vtx : VertexItem, undoable : bool) -> None:
        """
        Tidy up an existing vertex:
        - Merge existing vertices into one. Reattach existing segments.
        - Split and attach any segments that cross the vertex.
        - Remove duplicate segments.
        - Remove if the vertex breaks a simple straight line.
        - Remove if no segments are attached.
        """
        # start macro
        if undoable:
            self.undo_stack.beginMacro("tidyVertex")
        # get position
        pos = vtx.scenePos()
        # get existing vertices
        items = self.items(pos)
        xvtxs = [item for item in items if isinstance(item, VertexItem)]
        # connect existing segments to single vertex, remove existing vertices
        for xvtx in xvtxs:
            if xvtx is vtx:
                continue
            for seg in xvtx.connections():
                cmd = CmdReattachSegment(self, seg, xvtx, vtx)
                cmdExec(self, cmd, undoable)
            cmd = CmdRemoveVertex(self, xvtx)
            cmdExec(self, cmd, undoable)
        # split segments that cross the new vertex but are not attached to it
        segs = [item for item in items if isinstance(item, SegmentItem)]
        for seg in segs:
            # exclude segments attached to the clean vertex
            if seg.vtx1() is vtx or seg.vtx2() is vtx:
                continue
            # get far-end vertex (the one that will be detached)
            len1 = QLineF(seg.vtx1().scenePos(), vtx.scenePos()).length()
            len2 = QLineF(seg.vtx2().scenePos(), vtx.scenePos()).length()
            far = seg.vtx2() if len1 >= len2 else seg.vtx1()
            cmd = CmdReattachSegment(self, seg, far, vtx)
            cmdExec(self, cmd, undoable)
            # add new segment from split
            cmd = CmdAddSegment(self, vtx, far)
            cmdExec(self, cmd, undoable)
        # remove duplicate segments (that share the same vertices pair)
        segs = vtx.connections().copy()  # take copy because we're making changes
        if len(segs) > 1:
            for i, seg1 in enumerate(segs[:-1]):
                for seg2 in segs[i+1:]:
                    if (seg1.vtx1() is seg2.vtx1() and seg1.vtx2() is seg2.vtx2()) \
                    or (seg1.vtx1() is seg2.vtx2() and seg1.vtx2() is seg2.vtx1()):
                        cmd = CmdRemoveSegment(self, seg2)
                        cmdExec(self, cmd, undoable)
        # remove if useless break in a straight line
        segs = vtx.connections().copy()  # take copy because we're making changes
        if len(segs) == 2:
            # use scene-coordinate lines (seg.line() is local to each segment)
            sl0 = QLineF(segs[0].vtx1().scenePos(), segs[0].vtx2().scenePos())
            sl1 = QLineF(segs[1].vtx1().scenePos(), segs[1].vtx2().scenePos())
            if _colinear(sl0, sl1):
                # get far end of 2nd segment
                v2 = segs[1].vtx1() if segs[1].vtx2() is vtx else segs[1].vtx2()
                # reattach 1st segment to far end of 2nd segment
                cmd = CmdReattachSegment(self, segs[0], vtx, v2)
                cmdExec(self, cmd, undoable)
                # remove 2nd segment
                cmd = CmdRemoveSegment(self, segs[1])
                cmdExec(self, cmd, undoable)
        # remove if no connections
        if len(vtx.connections()) == 0:
            cmd = CmdRemoveVertex(self, vtx)
            cmdExec(self, cmd, undoable)
        # end macro
        if undoable:
            self.undo_stack.endMacro()

    def tidyConns(self : "DrawingScene", undoable : bool) -> None:
        """Tidy all connections in the scene."""
        items = self.items()
        segs = [item for item in items if isinstance(item, SegmentItem)]
        # tidy segments (replace QPointF with VertexItem)
        for seg in segs:
            v1 = seg.vtx1()
            if v1 is None:
                logger().warning(f"Segment {seg} has no vertex 1")
                seg.setVtx1(QPointF())
            if isinstance(v1, QPointF):
                seg.setVtx1(self.getVertex(v1, undoable))
            v2 = seg.vtx2()
            if v2 is None:
                logger().warning(f"Segment {seg} has no vertex 2")
                seg.setVtx2(QPointF())
            if isinstance(v2, QPointF):
                seg.setVtx2(self.getVertex(v2, undoable))
        # tidy vertices
        items = self.items()
        vtxs = [item for item in items if isinstance(item, VertexItem)]
        for vtx in vtxs:
            self.tidyVertex(vtx, undoable)

    def getVertex(
        self     : "DrawingScene",
        pos      : QPointF,
        undoable : bool = False
    ) -> VertexItem:
        """Get a vertex if present, add if necessary."""
        items = itemsTypeDict(self.items(pos))
        if VertexItem in items:
            vtxs = items[VertexItem]
            vtx = vtxs[0]
            if len(vtxs) > 1:
                self.tidyVertex(vtx, undoable)
        else:
            cmd = CmdAddVertex(self, pos)
            cmdExec(self, cmd, undoable)
            vtx = cmd.vtx()
        return vtx

    def addSegment(
        self     : "DrawingScene",
        p1       : QPointF,
        p2       : QPointF,
        undoable : bool = False
    ) -> None:
        """
        Add a segment, add vertices at any entries between endpoints, tidy.
        """
        # handle zero length - can happen on double click
        if p1 == p2:
            return  # do nothing
        # begin macro
        if undoable:
            self.undo_stack.beginMacro("addSegment")
        # get/create endpoint vertices
        v1 = self.getVertex(p1, undoable)
        v2 = self.getVertex(p2, undoable)
        # add segment
        cmd = CmdAddSegment(self, v1, v2)
        cmdExec(self, cmd, undoable)
        # get items along line, including endpoint vertices
        line_path = QPainterPath()
        line_path.moveTo(p1)
        line_path.lineTo(p2)
        stroker = QPainterPathStroker()
        stroker.setWidth(1.0)  # hit tolerance in scene units
        hit_path = stroker.createStroke(line_path)
        hit_items = self.items(hit_path)
        # tidy vertices — repeat until done
        vtxs = [item for item in hit_items if isinstance(item, VertexItem)]
        done = False
        while not done:
            done = True
            for vtx in vtxs:
                if vtx.scene() is not None:
                    self.tidyVertex(vtx, undoable)
                    if vtx.scene() is None:
                        done = False
        # end macro
        if undoable:
            self.undo_stack.endMacro()
