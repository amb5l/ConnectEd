"""
For movement rubber banding preview only.
"""

from __future__ import annotations

from typing import Self, Any, overload

from PyQt6.QtCore    import QLineF, QPointF
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PyQt6.QtGui     import QPainterPath

from ....core.check import checked
from ....core.types import Axis, Polarity

from .segment import SegmentItem
from .node    import NodeItem

from .role import ChromeItem

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

    def onSceneChanged(self : Self, scene : DrawingScene | None) -> None:
        if scene is None:
            return
        self.setPen(scene.resources.pen(self.resourcesName()))

    def geometry(self : Self) -> list[QLineF]:
        path = self.path()
        points : list[tuple[float, float]] = [
            (path.elementAt(i).x, path.elementAt(i).y)
            for i in range(path.elementCount())
        ]
        segs : list[QLineF] = []
        for (x0, y0), (x1, y1) in zip(points[:-1], points[1:], strict=False):
            if (x0, y0) == (x1, y1):
                continue
            p0 = self.mapToScene(QPointF(x0, y0))
            p1 = self.mapToScene(QPointF(x1, y1))
            segs.append(QLineF(p0, p1))
        return segs


class RubberTeeItem(ChromeItem, RubberItem):
    """
    For cases where a segment runs between a moving node and a T-junction on
    static perpendicular segments. A crossing is a special case of a T-junction.
    """

    # instance attributes
    _perp_lo   : float  # perpendicular segment lower coordinate
    _perp_hi   : float  # perpendicular segment upper coordinate

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
        junc_node = segment.otherNode(node)
        junc_spos = junc_node.scenePos()
        self.setPos(junc_spos)  # this item origin lies on junction
        # build perpendicular segment
        axis = segment.axis()
        self._axis = axis
        perp_p1 = junc_spos
        perp_p2 = perp_p1
        junc_segs = junc_node.segments()
        for junc_seg in junc_segs:
            if junc_seg is segment:
                continue
            junc_seg_axis = junc_seg.axis()
            if junc_seg_axis is None or junc_seg_axis == axis:
                continue
            new_p = junc_seg.otherNode(junc_node).scenePos()
            # update perp_p1 or perp_p2
            lx = QLineF(perp_p1, perp_p2).length()  # existing perp path length
            l1 = QLineF(new_p, perp_p2).length()    # length if perp_p1 => new_p
            l2 = QLineF(perp_p1, new_p).length()    # length if perp_p2 => new_p
            if l1 > lx or l2 > lx:
                perp_p1, perp_p2 = \
                    (new_p, perp_p2) if l1 > l2 else (perp_p1, new_p)
        self._perp_seg = QLineF(perp_p1, perp_p2)
        if axis == Axis.H:
            self._perp_lo = min(perp_p1.y(), perp_p2.y())
            self._perp_hi = max(perp_p1.y(), perp_p2.y())
        elif axis == Axis.V:
            self._perp_lo = min(perp_p1.x(), perp_p2.x())
            self._perp_hi = max(perp_p1.x(), perp_p2.x())
        # subscribe to node scene position changes
        node.subscribe("scenePos", self, "onGeometryChanged")
        # initialise path
        self.onGeometryChanged()

    @checked
    def onGeometryChanged(self : Self) -> None:
        node_pos = self._mobile.scenePos() - self.pos()
        x        = node_pos.x()
        y        = node_pos.y()
        lo       = self._perp_lo
        hi       = self._perp_hi
        path     = QPainterPath()
        if self._axis == Axis.H:
            sy = self._mobile.scenePos().y()
            if sy < lo or sy > hi:
                leader_y = (lo if sy < lo else hi) - self.pos().y()
                path.moveTo(0, leader_y)
                path.lineTo(0, y)
            else:
                path.moveTo(0, y)
            path.lineTo(x, y)
        elif self._axis == Axis.V:
            sx = self._mobile.scenePos().x()
            if sx < lo or sx > hi:
                leader_x = (lo if sx < lo else hi) - self.pos().x()
                path.moveTo(leader_x, 0)
                path.lineTo(x, 0)
            else:
                path.moveTo(x, 0)
            path.lineTo(x, y)
        else:
            path.moveTo(0, 0)
            path.lineTo(x, y)
        self.setPath(path)


class RubberCornerItem(ChromeItem, RubberItem):
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


class RubberJogItem(ChromeItem, RubberItem):
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
        return Polarity.POS if d >= 0 else Polarity.NEG

    @checked
    def inlineSpan(self : Self) -> tuple[float, float]:
        """Scene-coordinate endpoints of the jog along its inline axis."""
        ss = self._static.scenePos()
        ms = self._mobile.scenePos()
        if self._axis == Axis.H:
            lo, hi = ss.x(), ms.x()
        else:
            lo, hi = ss.y(), ms.y()
        return (min(lo, hi), max(lo, hi))

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
        dx = mobile_spos.x() - sx
        dy = mobile_spos.y() - sy
        path = QPainterPath()
        path.moveTo(0, 0)
        if self.isStraight() or self.isDegenerate():
            path.lineTo(dx, dy)
        elif self._axis == Axis.H:
            jog_x = self._lane - sx
            path.lineTo(jog_x, 0)
            path.lineTo(jog_x, dy)
            path.lineTo(dx, dy)
        elif self._axis == Axis.V:
            jog_y = self._lane - sy
            path.lineTo(0, jog_y)
            path.lineTo(dx, jog_y)
            path.lineTo(dx, dy)
        else:
            path.lineTo(dx, dy)
        self.setPath(path)
