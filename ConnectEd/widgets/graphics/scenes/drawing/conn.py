from math import isclose

from PyQt6.QtCore import QPointF, QLineF, QRectF

from .....app import logger

from .....core.utils import itemsTypeDict

from ...items.conn_vtx   import ConnVtx
from ...items.conn_seg   import ConnSeg
from ...items.node       import Node

from .cmd.conn import cmdAddConnVtx,     \
                      cmdRemoveConnVtx,  \
                      cmdAddConnSeg,     \
                      cmdRemoveConnSeg,  \
                      cmdReattachConnSeg

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingScene


################################################################################
# local helper functions
################################################################################


def _xp(point: QPointF, line: QLineF) -> float:
    """Returns the cross product magnitude for colinearity (should be ~0)."""
    if line.isNull():  # degenerate line (zero length)
        return point == line.p1()
    ap = point - line.p1()  # vector from p1 to point (AP)
    ab = line.p2() - line.p1()  # vector from p1 to p2 (AB)
    # cross product magnitude for collinearity (should be ~0)
    return ap.x() * ab.y() - ap.y() * ab.x()


def _setup_line_projection(line1: QLineF, line2: QLineF):
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


def _calculate_overlap_interval(other_line: QLineF, project_func):
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


def pointOnInfiniteLine(point: QPointF, line: QLineF, tol: float = 1e-6) -> bool:
    """Returns True if the point is on the infinite line."""
    cross_product = _xp(point, line)
    return isclose(cross_product, 0.0, abs_tol=tol)


def pointOnLine(point: QPointF, line: QLineF, tol: float = 1e-6) -> bool:
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


def colinear(line1: QLineF, line2: QLineF) -> bool:
    """
    Returns True if the lines are colinear.
    NOTE: they may or may not be touching or overlapping.
    """
    return \
        pointOnInfiniteLine(line1.p1(), line2) and \
        pointOnInfiniteLine(line1.p2(), line2) and \
        pointOnInfiniteLine(line2.p1(), line1) and \
        pointOnInfiniteLine(line2.p2(), line1)


def touching(line1: QLineF, line2: QLineF, tol: float = 1e-6) -> bool:
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


def overlapping(line1: QLineF, line2: QLineF) -> bool:
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

def dump(items):
    from ...items.junction import Junction
    for item in items:
        if isinstance(item, ConnSeg):
            print(" ConnSeg", item.vtx1().scenePos(), item.vtx2().scenePos())
        elif isinstance(item, ConnVtx):
            print(f" ConnVtx pos={item.pos()} scenePos={item.scenePos()}")
        elif isinstance(item, Junction):
            print(f" Junction pos={item.pos()} scenePos={item.scenePos()}")
        elif isinstance(item, Node):
            print(f" Node pos={item.pos()} scenePos={item.scenePos()}")
        else:
            print(" ", item)

################################################################################
# mixin
################################################################################


class DrawingSceneConnMixin:
    """Connection handling."""

    def tidyConnVtx(self : "DrawingScene", vtx : ConnVtx) -> None:
        """
        Tidy up an existing vertex:
        - Merge existing vertices into one new one. Reattach existing segments.
        - Parent to node if present.
        - Split and attach any segments that cross the vertex.
        - Remove duplicate segments.
        - Remove if the vertex breaks a simple straight line.
        - Remove if no segments are attached.
        """
        # start macro
        self.undo_stack.beginMacro("tidyConnVtx")
        # get position
        pos = vtx.scenePos()
        # get existing vertices
        items = self.items(pos)
        items_dict = itemsTypeDict(self.items(pos)) # get all items at position
        xvtxs : list[ConnVtx] = items_dict.get(ConnVtx, []) # get all vertices at position
        # create new clean vertex
        cmd = cmdAddConnVtx(self, pos)
        self.undo_stack.push(cmd)
        nvtx = cmd.vtx()
        # connect existing segments to new vertex
        for xvtx in xvtxs:
            for seg in xvtx.connections():
                self.undo_stack.push(cmdReattachConnSeg(self, seg, xvtx, nvtx))
            self.undo_stack.push(cmdRemoveConnVtx(self, xvtx))
        # parent to node if present
        nodes = [item for item in items if isinstance(item, Node)]
        if len(nodes) > 1:
            logger().warning("Multiple nodes found")
        if nodes:
            nvtx.setParentItem(nodes[0])
            nvtx.setPos(QPointF())  # pos is relative to node
        # split segments that cross the new vertex but are not attached to it
        segs = [item for item in items if isinstance(item, ConnSeg)]
        if ConnSeg in items_dict:
            for xseg in segs:
                # exclude segments that are already attached to the new vertex
                if xseg.vtx1() is nvtx or xseg.vtx2() is nvtx:
                    continue
                # get existing vertex (the one that will be detached)
                len1 = QLineF(xseg.vtx1().scenePos(), nvtx.scenePos()).length()
                len2 = QLineF(xseg.vtx2().scenePos(), nvtx.scenePos()).length()
                vtx = xseg.vtx2() if len1 >= len2 else xseg.vtx1()
                self.undo_stack.push(cmdReattachConnSeg(self, xseg, vtx, nvtx))
                # add new segment from split
                self.undo_stack.push(cmdAddConnSeg(self, nvtx, vtx))
        # remove duplicate segments
        segs = nvtx.connections().copy()  # copy to avoid race conditions
        if len(segs) > 1:
            for i, seg1 in enumerate(segs[:-1]):
                for seg2 in segs[i+1:]:
                    if seg1.vtx1() is seg2.vtx1() \
                    and seg1.vtx2() is seg2.vtx2():
                        self.undo_stack.push(cmdRemoveConnSeg(self, seg2))
        # remove if useless break in a straight line
        segs = nvtx.connections().copy()  # copy to avoid race conditions
        if len(segs) == 2 \
        and colinear(segs[0].toLine(), segs[1].toLine()) \
        and touching(segs[0].toLine(), segs[1].toLine()):
            # get far end of 2nd segment
            v2 = segs[1].vtx1() if segs[1].vtx2() is nvtx else segs[1].vtx2()
            # reattach 1st segment to far end of 2nd segment
            self.undo_stack.push(
                cmdReattachConnSeg(self, segs[0], nvtx, v2)
            )
            # remove 2nd segment
            self.undo_stack.push(cmdRemoveConnSeg(self, segs[1]))
            # remove new vertex
            self.undo_stack.push(cmdRemoveConnVtx(self, nvtx))
        # remove if no connections
        elif len(segs) == 0:
            self.undo_stack.push(cmdRemoveConnVtx(self, nvtx))
        # end macro
        self.undo_stack.endMacro()
        # debug
        items = self.items(pos)

    def addConnVtx(
        self : "DrawingScene",
        pos : QPointF
    ) -> None:
        """Add a vertex/junction, tidy."""
        self.undo_stack.beginMacro("addConnVtx")
        cmd = cmdAddConnVtx(self, pos)
        self.undo_stack.push(cmd)
        vtx = cmd.vtx()
        self.tidyConnVtx(vtx)

    def addConnSeg(
        self : "DrawingScene",
        p1   : QPointF,
        p2   : QPointF
    ) -> None:
        """
        Add a segment, add vertices at any nodes between endpoints, tidy.
        """
        # handle zero length - can happen on double click
        if p1 == p2:
            return  # do nothing
        # get items at start and end points
        items_dict_1 = itemsTypeDict(self.items(p1))
        items_dict_2 = itemsTypeDict(self.items(p2))
        # handle full overlap with an existing segment
        if ConnSeg in items_dict_1:
            if ConnSeg in items_dict_2:
                for seg1 in items_dict_1[ConnSeg]:
                    for seg2 in items_dict_2[ConnSeg]:
                        if seg1 is seg2:
                            return  # do nothing
        # begin macro
        self.undo_stack.beginMacro("addConnSeg")
        # add vertices at endpoint
        cmd = cmdAddConnVtx(self, p1)
        self.undo_stack.push(cmd)
        v1 = cmd.vtx()
        cmd = cmdAddConnVtx(self, p2)
        self.undo_stack.push(cmd)
        v2 = cmd.vtx()
        # add segment
        self.undo_stack.push(cmdAddConnSeg(self, v1, v2))
        # get bounding rect and line for segment
        rect = QRectF(p1, p2).normalized().adjusted(-1e-6, -1e-6, 1e-6, 1e-6)
        line = QLineF(p1, p2)
        # get items in rect
        items = self.items(rect)
        # get nodes in rect
        nodes = [item for item in items if isinstance(item, Node)]
        # get nodes that are on the line
        nodes = [node for node in nodes if pointOnLine(node.scenePos(), line)]
        # add vertices to unconnected nodes
        for node in nodes:
            children = node.childItems()
            child_vtxs = [item for item in children if isinstance(item, ConnVtx)]
            if len(child_vtxs) == 0:
                cmd = cmdAddConnVtx(self, QPointF())  # pos is relative to node
                self.undo_stack.push(cmd)
                vtx = cmd.vtx()
                vtx.setParentItem(node)
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
            self.tidyConnVtx(vtx)
        # end macro
        self.undo_stack.endMacro()
