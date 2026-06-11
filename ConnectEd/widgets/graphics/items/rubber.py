"""
For movement rubber banding preview only.
"""

from typing import Self, Any, overload

from PyQt6.QtCore    import QLineF
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PyQt6.QtGui     import QPainterPath

from ....core.check import checked
from ....core.types import Axis, Polarity

from .segment import SegmentItem
from .node    import NodeItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene


class RubberItem(QGraphicsPathItem):
    """Base class for rubber preview items."""
    _static    : NodeItem  # static node
    _mobile    : NodeItem  # mobile node
    _axis      : Axis      # connected segment axis

    def settingsName(self : Self) -> str:
        return "rubber"

    def resourcesName(self : Self) -> str:
        return self.settingsName()

    def __init__(self : Self) -> None:
        super().__init__()

    def itemChange(
        self   : Self,
        change : QGraphicsItem.GraphicsItemChange,
        value  : Any
    ) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemSceneHasChanged:
            if value is not None:
                self.onSceneChanged(value)
        return super().itemChange(change, value)

    def onSceneChanged(self : Self, scene : "DrawingScene | None") -> None:
        if scene is None:
            return
        self.setPen(scene.resources.pen(self.resourcesName()))

    def geometry(self : Self) -> list[QLineF]:
        origin = self._static.scenePos()  # not self.scenePos(); item may be off-scene
        ox     = origin.x()
        oy     = origin.y()
        path   = self.path()
        points : list[tuple[float, float]] = [
            (path.elementAt(i).x, path.elementAt(i).y)
            for i in range(path.elementCount())
        ]
        segs : list[QLineF] = []
        for (x0, y0), (x1, y1) in zip(points[:-1], points[1:], strict=False):
            if (x0, y0) == (x1, y1):
                continue
            segs.append(QLineF(x0 + ox, y0 + oy, x1 + ox, y1 + oy))
        return segs


class RubberTeeItem(RubberItem):
    """
    For cases where a segment runs between a moving node and a T-junction on
    static perpendicular segments. A crossing is a special case of a T-junction.
    """

    # instance attributes
    _perp_lo   : float     # perpendicular segment lower coordinate
    _perp_hi   : float     # perpendicular segment upper coordinate

    @checked
    def __init__(
        self    : Self,
        segment : SegmentItem,  # segment to be rubberized
        node    : NodeItem      # mobile node at end of segment
    ) -> None:
        # initialise superclass
        super().__init__()
        # set instance attributes
        self._static = segment.otherNode(node)
        self._mobile = node
        # positioning
        node_spos = node.scenePos()
        junc_spos = segment.otherNode(node).scenePos()
        self.setPos(junc_spos)  # this item origin lies on junction
        # initialise path
        path = QPainterPath()
        path.moveTo(0, 0)  # initially redundant, may change later
        path.lineTo(0, 0)  # initially redundant, may change later
        path.lineTo(node_spos - junc_spos)
        self.setPath(path)
        # build perpendicular segment
        axis = segment.axis(node)
        self._axis = axis
        perp_p1 = junc_spos
        perp_p2 = perp_p1
        junc_segs = node.segments()
        for perp_seg in junc_segs:
            seg_axis = perp_seg.axis()
            if seg_axis is None or seg_axis == ~axis:
                continue
            new_p = perp_seg.otherNode(node).scenePos()
            # update perp_p1 or perp_p2
            lx = QLineF(perp_p1, perp_p2).length()  # existing perp path length
            l1 = QLineF(new_p, perp_p2).length()    # length if perp_p1 => new_p
            l2 = QLineF(perp_p1, new_p).length()    # length if perp_p2 => new_p
            if l1 > lx or l2 > lx:
                perp_p1, perp_p2 = new_p, perp_p2 if l1 > l2 else new_p, perp_p2
        self._perp_seg = QLineF(perp_p1, perp_p2)
        # subscribe to node scene position changes
        node.subscribe("scenePos", self, "onGeometryChanged")

    def onGeometryChanged(self : Self) -> None:
        # update path
        path = self.path()
        node_spos = self._mobile.scenePos()
        node_pos = node_spos - self.pos()
        if self._axis == Axis.H:
            y = node_pos.y()
            if y < self._perp_lo or y > self._perp_hi:
                # leader from existing perpendicular segment is required
                leader_y = self._perp_lo if y < self._perp_lo else self._perp_hi
                path.setElementPositionAt(0, 0, leader_y)  # moveTo
                path.setElementPositionAt(1, 0, y)         # lineTo
            else:
                # no leader
                path.setElementPositionAt(0, 0, y)  # moveTo
                path.setElementPositionAt(1, 0, y)  # lineTo
            path.setElementPositionAt(2, node_pos.x(), y)  # lineTo
        elif self._axis == Axis.V:
            x = node_pos.x()
            if x < self._perp_lo or x > self._perp_hi:
                # leader from existing perpendicular segment is required
                leader_x = self._perp_lo if x < self._perp_lo else self._perp_hi
                path.setElementPositionAt(0, leader_x, 0)  # moveTo
                path.setElementPositionAt(1, x, 0)         # lineTo
            else:
                # no leader
                path.setElementPositionAt(0, x, 0)  # moveTo
                path.setElementPositionAt(1, x, 0)  # lineTo
            path.setElementPositionAt(2, x, node_pos.y())  # lineTo
        self.setPath(path)


class RubberCornerItem(RubberItem):
    """
    For cases where a segment runs between a moving node and a corner with
    a perpendicular segment.
    """

    @checked
    def __init__(
        self     : Self,
        segment1 : SegmentItem,  # segment 1 to be rubberized
        segment2 : SegmentItem,  # segment 2 to be rubberized
        node     : NodeItem      # mobile node at end of segment 1
    ) -> None:
        # initialise superclass
        super().__init__()
        # positioning
        node_spos = node.scenePos()
        corner_node = segment1.otherNode(node)
        corner_spos = corner_node.scenePos()
        origin_node = segment2.otherNode(corner_node)
        origin_spos = origin_node.scenePos()
        self.setPos(origin_spos)
        # set instance attributes
        self._static = origin_node
        self._mobile = node
        self._axis   = segment1.axis()
        # initialise path
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(corner_spos - origin_spos)
        path.lineTo(node_spos - origin_spos)
        self.setPath(path)
        # subscribe to node scene position changes
        node.subscribe("scenePos", self, "onGeometryChanged")

    def onGeometryChanged(self : Self) -> None:
        # update path
        path = self.path()
        node_spos = self._mobile.scenePos()
        node_pos = node_spos - self.pos()
        x = node_pos.x()
        y = node_pos.y()
        if self._axis == Axis.H:
            path.setElementPositionAt(1, 0, y)
            path.setElementPositionAt(2, x, y)
        else:
            path.setElementPositionAt(1, x, 0)
            path.setElementPositionAt(2, x, y)
        self.setPath(path)


class RubberJogItem(RubberItem):
    """
    For cases where a segment runs between a moving node and a fixed node.
    Draws a single step from static to mobile node (inline/across/inline).
    Assumes static node does not move for item lifetime.
    """

    # instance attributes
    _pol    : Polarity  # axis direction (+ or -)
    _lane   : float     # scene coordinate of jog lane

    @overload
    def __init__(
        self    : Self,
        segment : SegmentItem,
        mobile  : NodeItem,
        axis    : Axis | None = None
    ) -> None:
        ...

    @overload
    def __init__(
        self   : Self,
        static : NodeItem,
        mobile : NodeItem,
        axis   : Axis | None = None
    ) -> None:
        ...

    @checked
    def __init__(
        self              : Self,
        segment_or_static : SegmentItem | NodeItem,
        mobile            : NodeItem,
        axis              : Axis | None = None
    ) -> None:
        """
        Rubber jog (step) item between a static and mobile node.

        Args:
            segment_or_static: Segment being rubberized or static node.
            mobile:            Mobile node.
        """
        # assumption: nodes are initially colinear on H or V line
        # initialise superclass
        super().__init__()
        # get coordinates
        if isinstance(segment_or_static, SegmentItem):
            segment = segment_or_static
            static = segment.otherNode(mobile)
            axis = segment.axis()  # override arg if supplied
        elif isinstance(segment_or_static, NodeItem):
            static = segment_or_static
        static_spos = static.scenePos()
        sx = static_spos.x()
        sy = static_spos.y()
        mobile_spos = mobile.scenePos()
        mx = mobile_spos.x()
        my = mobile_spos.y()
        # record nodes
        self._static = static
        self._mobile = mobile
        # record axis
        if axis is None:
            axis = Axis.H if sy == my else Axis.V if sx == mx else None
        self._axis = axis
        # record polarity
        if axis == Axis.H:
            pol = Polarity.POS if sx < mx else Polarity.NEG
        elif axis == Axis.V:
            pol = Polarity.POS if sy < my else Polarity.NEG
        else:
            pol = Polarity.POS
        self._pol = pol
        # assign initial jog lane
        lane = (sx + mx) / 2 if axis == Axis.H else (sy + my) / 2
        self._lane = lane
        # initialise position and path
        self.setPos(static_spos)
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(0, 0)
        path.lineTo(0, 0)
        path.lineTo(0, 0)
        self.updatePath()

    @checked
    def axis(self : Self) -> Axis:
        return self._axis

    @checked
    def inlinePolarity(self : Self) -> Polarity:
        return self._pol

    @checked
    def acrossPolarity(self : Self) -> Polarity:
        ss = self._static.scenePos()  # not self.scenePos() (self not in scene)
        ms = self._mobile.scenePos()
        d = ms.y() - ss.y() if self._axis == Axis.H else ms.x() - ss.x()
        return Polarity.POS if d > 0 else Polarity.NEG if d < 0 else None

    @checked
    def inlineDistance(self : Self) -> float:
        """
        Distance from static to mobile node along inline axis.
        """
        ss = self._static.scenePos()
        ms = self._mobile.scenePos()
        a = self._axis
        p = self._pol
        if a == Axis.H:
            return ms.x() - ss.x() if p == Polarity.POS else ss.x() - ms.x()
        elif a == Axis.V:
            return ms.y() - ss.y() if p == Polarity.POS else ss.y() - ms.y()
        else:
            return 0

    @checked
    def acrossDistance(self : Self) -> float:
        """
        Distance from static to mobile node across inline axis.
        """
        ss = self._static.scenePos()
        ms = self._mobile.scenePos()
        a = self._axis
        p = self._pol
        if a == Axis.H:
            return ms.x() - ss.x() if p == Polarity.POS else ss.x() - ms.x()
        elif a == Axis.V:
            return ms.y() - ss.y() if p == Polarity.POS else ss.y() - ms.y()
        else:
            return 0

    @checked
    def acrossCenter(self: Self) -> float:
        """Center of the across span (used for spatial ordering)."""
        ss = self._static.scenePos()
        ms = self._mobile.scenePos()
        if self._axis == Axis.H:
            return (ss.y() + ms.y()) / 2
        return (ss.x() + ms.x()) / 2

    @checked
    def isStraight(self: Self) -> bool:
        return self.acrossDistance() == 0

    @checked
    def isDegenerate(self: Self) -> bool:
        return self._lane is None

    @checked
    def prefLane(self: Self) -> float:
        """
        Midpoint lane the jog would like if unconstrained.
        """
        ss = self._static.scenePos()
        ms = self._mobile.scenePos()
        if self._axis == Axis.H:
            return (ss.x() + ms.x()) / 2
        return (ss.y() + ms.y()) / 2

    @checked
    def lane(self : Self) -> float | None:
        return self._lane

    @checked
    def setLane(self : Self, lane : float | None)  -> None:
        self._lane = lane
        self.updatePath()

    def updatePath(self : Self) -> None:
        static_spos = self._static.scenePos()
        sx = static_spos.x()
        sy = static_spos.y()
        mobile_spos = self._mobile.scenePos()
        mx = mobile_spos.x()
        my = mobile_spos.y()
        path = self.path()
        path.setElementPositionAt(0, 0, 0)
        if self.isStraight() or self.isDegenerate():
            path.setElementPositionAt(1, 0, 0)
            path.setElementPositionAt(2, 0, 0)
        elif self._axis == Axis.H:
            jog_x = self._lane - sx
            path.setElementPositionAt(1, jog_x, 0)
            path.setElementPositionAt(2, jog_x, my - sy)
        elif self._axis == Axis.V:
            jog_y = self._lane - sy
            path.setElementPositionAt(1, 0, jog_y)
            path.setElementPositionAt(2, mx - sx, jog_x)
        path.setElementPositionAt(3, mx - sx, my - sy)
        self.setPath(path)
