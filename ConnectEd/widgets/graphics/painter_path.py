from typing import Self, overload
from math import sqrt, degrees, radians, sin, cos, atan2

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui  import QPainterPath

from ...core.utils import sign


class PainterPath(QPainterPath):
    """QPainterPath with enhanced arcTo method."""

    # instance attributes
    _mid_pos : QPointF | None  # latest line/arc midpoint
    _angle   : float | None    # angle of latest line/arc chord

    def __init__(self : Self) -> None:
        super().__init__()
        self._mid_pos = None
        self._angle = None

    def lineTo(self : Self, pos : QPointF) -> None:
        """Override to store midpoint."""
        p0 = self.currentPosition()
        super().lineTo(pos)
        self._mid_pos = (pos + p0) / 2
        self._angle = degrees(atan2(pos.y() - p0.y(), pos.x() - p0.x()))

    @overload
    def arcTo(
        self       : Self,
        rect       : QRectF,
        startAngle : float,  # noqa: N803
        spanAngle  : float   # noqa: N803
    ) -> None:
        ...

    @overload
    def arcTo(
        self      : Self,
        pos       : QPointF,
        spanAngle : float   # noqa: N803
    ) -> None:
        ...

    def arcTo(
        self : Self,
        a1   : QRectF | QPointF,
        a2   : float,
        a3   : float | None = None
    ) -> None:
        if isinstance(a1, QRectF):
            # rect, startAngle, spanAngle
            rect = a1
            startAngle = a2  # noqa: N806
            spanAngle = a3   # noqa: N806
        else:
            # pos, sweep
            p1 = self.currentPosition()
            p2 = a1
            spanAngle = max(-180, min(180, a2))  # noqa: N806
            # chord
            x1 = p1.x()
            y1 = p1.y()
            x2 = p2.x()
            y2 = p2.y()
            dx = x2 - x1  # vector x
            dy = y2 - y1  # vector y
            d = sqrt(dx**2 + dy**2)  # length
            if d < 0.001:  # degenerate case
                self.lineTo(p2)
            mx = (x1 + x2) / 2  # midpoint x
            my = (y1 + y2) / 2  # midpoint y
            # arc circle radius
            r = d / (2 * sin(radians(abs(spanAngle) / 2)))
            # chord midpoint to arc circle center distance
            h = sqrt(r**2 - (d / 2)**2)
            # perpendicular unit vector
            ux = sign(spanAngle) *  dy / d
            uy = sign(spanAngle) * -dx / d
            # arc circle center
            cx = mx + (ux * h)
            cy = my + (uy * h)
            # arc circle bounding rect
            rect = QRectF(cx - r, cy - r, 2 * r, 2 * r)
            # calculate start angle
            c1x = x1 - cx
            c1y = y1 - cy
            startAngle = degrees(atan2(-c1y, c1x))  # noqa: N806
            # store chord angle and arc midpoint
            a = radians(startAngle + (spanAngle / 2))
            self._mid_pos = QPointF(cx + (r * cos(a)), cy - (r * sin(a)))
            self._angle = degrees(atan2(dy, dx))
        return super().arcTo(rect, startAngle, spanAngle)

    def currentMidPos(self : Self) -> QPointF | None:
        """Midpoint of latest line or arc."""
        return self._mid_pos

    def currentAngle(self : Self) -> float | None:
        """Angle of latest line or arc chord."""
        return self._angle
