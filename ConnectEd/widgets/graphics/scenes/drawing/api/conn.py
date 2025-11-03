from typing import Callable
from math   import isclose

from PyQt6.QtCore import QPointF, QLineF, QRectF

from ......app import logger

from ......core.utils import itemsTypeDict

from ....items.conn_vtx import ConnVtx
from ....items.conn_seg import ConnSeg
from ....items.entry    import Entry

from ..cmd      import cmdExec
from ..cmd.conn import CmdAddConnVtx,      \
                       CmdReparentConnVtx, \
                       CmdRemoveConnVtx,   \
                       CmdAddConnSeg,      \
                       CmdReattachConnSeg, \
                       CmdRemoveConnSeg

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


################################################################################
# local helper functions
################################################################################


def _xp(point : QPointF, line : QLineF) -> float:
    """Returns the cross product magnitude for colinearity (should be ~0)."""
    if line.isNull():  # degenerate line (zero length)
        return point == line.p1()
    ap = point - line.p1()  # vector from p1 to point (AP)
    ab = line.p2() - line.p1()  # vector from p1 to p2 (AB)
    # cross product magnitude for collinearity (should be ~0)
    return ap.x() * ab.y() - ap.y() * ab.x()


def _setup_line_projection(
    line1 : QLineF,
    line2 : QLineF
) -> tuple[QLineF, QLineF, Callable[[QPointF], float]]:
    """
    Setup projection calculation for two colinear lines.
    Returns (base_line, other_line, projection_function),
    where base is the longer line.
    """
    if line1.isNull() or line2.isNull():
        return None, None, None
    # choose the longer line as base for better numerical stability
    len1 = line1.length()
    len2 = line2.length()
    if len1 >= len2:
        base = line1
        other = line2
    else:
        base = line2
        other = line1
    # compute projection setup
    base_p1 = base.p1()
    base_vec = base.p2() - base_p1
    len_squared = base_vec.x()**2 + base_vec.y()**2  # >0 since not null
    # compute projection function
    def project(point: QPointF) -> float:
        ap = point - base_p1
        dot = ap.x() * base_vec.x() + ap.y() * base_vec.y()
        return dot / len_squared
    return base, other, project


def _calculate_overlap_interval(
    other_line   : QLineF,
    project_func : Callable[[QPointF], float]
) -> tuple[float, float]:
    """
    Calculate the overlap interval in parameter space [0,1].
    Returns (start_overlap, end_overlap).
    """
    t_start = project_func(other_line.p1())
    t_end = project_func(other_line.p2())
    min_t = min(t_start, t_end)
    max_t = max(t_start, t_end)
    # compute overlap interval in parameter space
    start_overlap = max(0.0, min_t)
    end_overlap = min(1.0, max_t)
    # touching if overlap degenerates to a point (within tol)
    return start_overlap, end_overlap


################################################################################
# local functions
################################################################################


def pointOnInfiniteLine(
    point : QPointF,
    line  : QLineF,
    tol   : float = 1e-6
) -> bool:
    """Returns True if the point is on the infinite line."""
    cross_product = _xp(point, line)
    return isclose(cross_product, 0.0, abs_tol=tol)


def pointOnLine(point : QPointF, line : QLineF, tol : float = 1e-6) -> bool:
    """Returns True if the point is on the finite line."""
    cross_product = _xp(point, line)
    if not isclose(cross_product, 0.0, abs_tol=tol):
        return False
    # check if point is within the segment bounds (project onto line)
    ap = point - line.p1()
    ab = line.p2() - line.p1()
    dot_product = ap.x() * ab.x() + ap.y() * ab.y()
    len_squared = ab.x()**2 + ab.y()**2
    if len_squared == 0:
        return isclose(point.x(), line.p1().x(), abs_tol=tol) and \
            isclose(point.y(), line.p1().y(), abs_tol=tol)
    projection = dot_product / len_squared
    return 0.0 <= projection <= 1.0


def colinear(line1 : QLineF, line2 : QLineF) -> bool:
    """
    Returns True if the lines are colinear.
    NOTE: they may or may not be touching or overlapping.
    """
    return \
        pointOnInfiniteLine(line1.p1(), line2) and \
        pointOnInfiniteLine(line1.p2(), line2) and \
        pointOnInfiniteLine(line2.p1(), line1) and \
        pointOnInfiniteLine(line2.p2(), line1)


def touching(line1 : QLineF, line2 : QLineF, tol : float = 1e-6) -> bool:
    """Returns True if the lines are touching, but not overlapping."""
    if not colinear(line1, line2):
        return False
    # setup projection calculation
    _base, other, project = _setup_line_projection(line1, line2)
    if project is None:
        return False
    # calculate overlap interval
    start_overlap, end_overlap = _calculate_overlap_interval(other, project)
    # touching if overlap degenerates to a point (within tol)
    return isclose(start_overlap, end_overlap, abs_tol=tol)


def overlapping(line1 : QLineF, line2 : QLineF) -> bool:
    """Returns True if the lines are overlapping, not just touching."""
    if not colinear(line1, line2):
        return False
    # setup projection calculation
    _base, other, project = _setup_line_projection(line1, line2)
    if project is None:
        return False
    # calculate overlap interval
    start_overlap, end_overlap = _calculate_overlap_interval(other, project)
    # overlapping if positive overlap length (strict > for not just touching)
    return start_overlap < end_overlap

################################################################################
# mixin
################################################################################


class DrawingSceneApiConnMixin:
    """Connection handling."""

    def tidyConnVtx(self : "DrawingScene", vtx : ConnVtx, undoable : bool) -> None:
        """
        Tidy up an existing vertex:
        - Merge existing vertices into one. Reattach existing segments.
        - Parent to entry if present.
        - Split and attach any segments that cross the vertex.
        - Remove duplicate segments.
        - Remove if the vertex breaks a simple straight line.
        - Remove if no segments are attached.
        """
        # start macro
        if undoable:
            self.undo_stack.beginMacro("tidyConnVtx")
        # get position
        pos = vtx.scenePos()
        # get existing vertices
        items = self.items(pos)
        xvtxs = [item for item in items if isinstance(item, ConnVtx)]
        # pick oldest existing vertex to be clean single vertex
        vtx1 = xvtxs[-1]
        # connect existing segments to single vertex, remove existing vertices
        for xvtx in xvtxs:
            if xvtx is vtx1:
                continue
            for seg in xvtx.connections():
                cmd = CmdReattachConnSeg(self, seg, xvtx, vtx1)
                cmdExec(self, cmd, undoable)
            cmd = CmdRemoveConnVtx(self, xvtx)
            cmdExec(self, cmd, undoable)
        # (re)parent to entry if present
        entries = [item for item in items if isinstance(item, Entry)]
        if len(entries) > 1:
            logger().warning("Multiple entries found")
        if entries:
            if vtx1.parentItem() is not entries[0]:
                cmd = CmdReparentConnVtx(self, vtx1, entries[0])
                cmdExec(self, cmd, undoable)
        # split segments that cross the new vertex but are not attached to it
        segs = [item for item in items if isinstance(item, ConnSeg)]
        for seg in segs:
            # exclude segments attached to the clean vertex
            if seg.vtx1() is vtx1 or seg.vtx2() is vtx1:
                continue
            # get existing vertex (the one that will be detached)
            len1 = QLineF(seg.vtx1().scenePos(), vtx1.scenePos()).length()
            len2 = QLineF(seg.vtx2().scenePos(), vtx1.scenePos()).length()
            vtx = seg.vtx2() if len1 >= len2 else seg.vtx1()
            cmd = CmdReattachConnSeg(self, seg, vtx, vtx1)
            cmdExec(self, cmd, undoable)
            # add new segment from split
            cmd = CmdAddConnSeg(self, vtx1, vtx)
            cmdExec(self, cmd, undoable)
        # remove duplicate segments (that share the same vertices pair)
        segs = vtx1.connections().copy()  # take copy because we're making changes
        if len(segs) > 1:
            for i, seg1 in enumerate(segs[:-1]):
                for seg2 in segs[i+1:]:
                    if (seg1.vtx1() is seg2.vtx1() and seg1.vtx2() is seg2.vtx2()) \
                    or (seg1.vtx1() is seg2.vtx2() and seg1.vtx2() is seg2.vtx1()):
                        cmd = CmdRemoveConnSeg(self, seg2)
                        cmdExec(self, cmd, undoable)
        # remove if useless break in a straight line
        segs = vtx1.connections().copy()  # take copy because we're making changes
        if len(segs) == 2:
            if colinear(segs[0].line(), segs[1].line()) \
            and touching(segs[0].line(), segs[1].line()):
                # get far end of 2nd segment
                v2 = segs[1].vtx1() if segs[1].vtx2() is vtx1 else segs[1].vtx2()
                # reattach 1st segment to far end of 2nd segment
                cmd = CmdReattachConnSeg(self, segs[0], vtx1, v2)
                cmdExec(self, cmd, undoable)
                # remove 2nd segment
                cmd = CmdRemoveConnSeg(self, segs[1])
                cmdExec(self, cmd, undoable)
        # remove if no connections
        if len(vtx1.connections()) == 0:
            cmd = CmdRemoveConnVtx(self, vtx1)
            cmdExec(self, cmd, undoable)
        # end macro
        if undoable:
            self.undo_stack.endMacro()

    def tidyConns(self : "DrawingScene", undoable : bool) -> None:
        """Tidy all connections in the scene."""
        items = self.items()
        segs = [item for item in items if isinstance(item, ConnSeg)]
        # tidy segments (replace QPointF with ConnVtx)
        for seg in segs:
            v1 = seg.vtx1()
            if v1 is None:
                logger().warning(f"Segment {seg} has no vertex 1")
                seg.setVtx1(QPointF())
            if isinstance(v1, QPointF):
                seg.setVtx1(self.addConnVtx(v1, undoable))
            v2 = seg.vtx2()
            if v2 is None:
                logger().warning(f"Segment {seg} has no vertex 2")
                seg.setVtx2(QPointF())
            if isinstance(v2, QPointF):
                seg.setVtx2(self.addConnVtx(v2, undoable))
        # tidy vertices
        items = self.items()
        vtxs = [item for item in items if isinstance(item, ConnVtx)]
        for vtx in vtxs:
            self.tidyConnVtx(vtx, undoable)

    def addConnVtx(
        self     : "DrawingScene",
        pos      : QPointF,
        undoable : bool = False,
        cls      : type[ConnVtx] = ConnVtx
    ) -> ConnVtx:
        """Add a vertex/junction."""
        # add vertex
        cmd = CmdAddConnVtx(self, pos, cls)
        cmdExec(self, cmd, undoable)
        return cmd.vtx()

    def addConnSeg(
        self     : "DrawingScene",
        p1       : QPointF,
        p2       : QPointF,
        undoable : bool = False,
        cls      : type[ConnSeg] = ConnSeg
    ) -> ConnSeg | None:
        """
        Add a segment, add vertices at any entries between endpoints, tidy.
        """
        # begin macro
        if undoable:
            self.undo_stack.beginMacro("addConnSeg")
        # handle zero length - can happen on double click
        if p1 == p2:
            return None  # do nothing
        # get items at start and end points
        items_dict_1 = itemsTypeDict(self.items(p1))
        items_dict_2 = itemsTypeDict(self.items(p2))
        # handle full overlap with an existing segment
        if ConnSeg in items_dict_1:
            if ConnSeg in items_dict_2:
                for seg1 in items_dict_1[ConnSeg]:
                    for seg2 in items_dict_2[ConnSeg]:
                        if seg1 is seg2:
                            return None  # do nothing
        # add vertices at endpoint
        cmd = CmdAddConnVtx(self, p1)
        cmdExec(self, cmd, undoable)
        v1 = cmd.vtx()
        cmd = CmdAddConnVtx(self, p2)
        cmdExec(self, cmd, undoable)
        v2 = cmd.vtx()
        # add segment
        cmd = CmdAddConnSeg(self, v1, v2, cls)
        cmdExec(self, cmd, undoable)
        seg = cmd.seg()
        # get bounding rect and line for segment
        rect = QRectF(p1, p2).normalized().adjusted(-1e-6, -1e-6, 1e-6, 1e-6)
        line = QLineF(p1, p2)
        # get items in rect
        items = self.items(rect)
        # get entries in rect
        entries = [item for item in items if isinstance(item, Entry)]
        # get entries that are on the line
        entries = [entry for entry in entries if pointOnLine(entry.scenePos(), line)]
        # add vertices to unconnected entries
        for entry in entries:
            children = entry.childItems()
            child_vtxs = [item for item in children if isinstance(item, ConnVtx)]
            if len(child_vtxs) == 0:
                cmd = CmdAddConnVtx(self, QPointF())  # pos is relative to entry
                cmdExec(self, cmd, undoable)
                vtx = cmd.vtx()
                vtx.setParentItem(entry)
        # get all vertices in rect
        vtxs = [item for item in items if isinstance(item, ConnVtx)]
        # get vertices that are on the line
        vtxs = [vtx for vtx in vtxs if pointOnLine(vtx.scenePos(), line)]
        # sort by distance from p1 (TODO: is this needed?)
        vtxs.sort(key=lambda vtx: QLineF(p1, vtx.scenePos()).length())
        # basic checks before finishing
        if len(vtxs) < 2:
            logger().warning(f"Less than 2 vertices on line: {len(vtxs)}")
        elif vtxs[0].scenePos() != p1:
            logger().warning(f"First vertex on line is not at p1: {vtxs[0].scenePos()}")
        elif vtxs[-1].scenePos() != p2:
            logger().warning(f"Last vertex on line is not at p2: {vtxs[-1].scenePos()}")
        # tidy all vertices on line
        for vtx in vtxs:
            self.tidyConnVtx(vtx, undoable)
        # end macro
        if undoable:
            self.undo_stack.endMacro()
        # done
        return seg
