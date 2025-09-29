from typing import Self

from PyQt6.QtCore    import QPointF, QLineF, QRectF
from PyQt6.QtWidgets import QGraphicsItem

from ......app import logger

from ....items.wire_vertex import WireVertex
from ....items.node        import Node

from ....items.wire_segment import WireSegment

from . import cmdSceneBase, cmdSelectionMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class cmdAddWireSubSegment(cmdSceneBase):
    """Command to add a wire sub-segment. No splitting."""

    # instance attributes
    _v1  : WireVertex
    _v2  : WireVertex
    _p1  : QPointF      # position of v1 (where not in scene)
    _p2  : QPointF      # position of v2 (where not in scene)
    _seg : WireSegment

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        v1    : WireVertex,
        v2    : WireVertex
    ) -> None:
        super().__init__(scene)
        self._v1 = v1
        self._v2 = v2
        self._p1 = v1.pos() if v1.scene() != scene else None
        self._p2 = v2.pos() if v2.scene() != scene else None

    def redo(self : Self) -> None:
        if self._p1 is not None:
            self._v1 = WireVertex()
            self._v1.setPos(self._p1)
            self._scene.addItem(self._v1)
        if self._p2 is not None:
            self._v2 = WireVertex()
            self._v2.setPos(self._p2)
            self._scene.addItem(self._v2)
        self._seg = WireSegment(self._v1, self._v2)
        self._scene.addItem(self._seg)

    def undo(self : Self) -> None:
        # remove segment
        self._scene.removeItem(self._seg)
        # remove vertices if they were not already in scene
        if self._p2 is not None:
            self._scene.removeItem(self._v2)
        if self._p1 is not None:
            self._scene.removeItem(self._v1)


class cmdAddWireSegment(cmdSceneBase, cmdSelectionMixin):
    """Command to add a wire segment, splitting/merging as needed."""

    # instance attributes
    _p1   : QPointF
    _p2   : QPointF
    _term : bool

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        p1    : QPointF,
        p2    : QPointF
    ):
        super().__init__(scene)
        self._preserveSelection([])
        self._p1   = p1
        self._p2   = p2
        self._term = False

    def redo(self : Self) -> None:
        """Creates sub segments as needed."""

        if self._p1 == self._p2:
            logger().warning("Start and end points are the same")
            return  # do nothing

        def pointOnLine(point: QPointF, line: QLineF, tol: float = 1e-6) -> bool:
            """Returns True if the point is on the line."""
            if line.isNull():  # degenerate line (zero length)
                return abs(point - line.p1()) < tol
            ap = point - line.p1()  # vector from p1 to point (AP)
            ab = line.p2() - line.p1()  # vector from p1 to p2 (AB)
            # cross product magnitude for collinearity (should be ~0)
            cross = ap.x() * ab.y() - ap.y() * ab.x()
            return abs(cross) <= tol * line.length()

        def getWireVertex(pos: QPointF, items: list[QGraphicsItem]) -> WireVertex:
            """Return existing or new wire vertex at position."""
            pos_items = [i for i in items if i.scenePos() == pos]
            if pos_items:
                item_types = set(type(item) for item in pos_items)
                if Node in item_types:
                    for item in pos_items:
                        if isinstance(item, Node):
                            return WireVertex(item)
                elif WireVertex in item_types:
                    for item in pos_items:
                        if isinstance(item, WireVertex):
                            return item
            v = WireVertex()
            v.setPos(pos)
            return v

        # begin macro
        self._scene.undo_stack.beginMacro("Add Wire Segment")
        # get rectangle formed by segment start and end points
        # (will normally have zero width or height c.w. h/v line)
        rect = QRectF(self._p1, self._p2).normalized()
        # get all items in rect
        items = self._scene.items(rect)
        # exclude items except WireVertex and Node
        items = [i for i in items if isinstance(i, WireVertex | Node)]
        # exclude items not on the line
        items = [i for i in items if pointOnLine(i.pos(), seg.line())]
        # get unique positions using tuples as keys to avoid duplicates
        position_dict = {}
        position_dict[(self._p1.x(), self._p1.y())] = self._p1
        position_dict[(self._p2.x(), self._p2.y())] = self._p2
        for item in items:
            pos = item.scenePos()
            position_dict[(pos.x(), pos.y())] = pos
        # convert back to list and sort by distance from start point
        positions = list(position_dict.values())
        positions.sort(key=lambda x: QLineF(self._p1, x).length())
        # process start point
        v1 = getWireVertex(self._p1, items)
        # remove start position
        positions.remove(self._p1)
        # process remaining positions up to end point, creating sub segments
        for pos in positions:
            v2 = getWireVertex(pos, items)
            self._scene.undo_stack.push(cmdAddWireSubSegment(
                self._scene, v1, v2
            ))
            v1 = v2
        # at this point, v1 is the last vertex in the segment;
        #  use it to indicate whether the segment is terminated
        self._term = v1.scene() == self._scene
        # end macro
        self._scene.undo_stack.endMacro()

    def undo(self : Self) -> None:
        # macro is automatically undone
        self._restoreSelection()
        self._term = False

    def terminated(self : Self) -> bool:
        return self._term
