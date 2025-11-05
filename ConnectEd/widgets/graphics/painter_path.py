from typing import Self, overload
from math import copysign, sqrt, degrees, radians, sin, cos, asin, atan2

from PyQt6.QtCore import QPointF, QLineF, QRectF
from PyQt6.QtGui  import QPainterPath

from ...core.utils import sign


class PainterPath(QPainterPath):
    """QPainterPath with enhanced arc and grip support."""

    # instance attributes
    _mid_pos : QPointF | None  # latest line/arc midpoint
    _angle   : float | None    # angle of latest line/arc chord

    def __init__(self : Self) -> None:
        super().__init__()
        self._mid_pos = None
        self._angle = None

    @overload
    def lineTo(self : Self, pos : QPointF) -> None:
        ...

    @overload
    def lineTo(self : Self, x : float, y : float) -> None:
        ...

    def lineTo(self : Self, *args) -> None:
        """Override to store midpoint. Accepts QPointF or (x, y) coordinates."""
        if len(args) == 1 and isinstance(args[0], QPointF):
            pos = args[0]
        elif len(args) == 2:
            pos = QPointF(float(args[0]), float(args[1]))
        else:
            raise TypeError("lineTo() takes either QPointF or (x, y) coordinates")
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
        self       : Self,
        x          : float,
        y          : float,
        width      : float,
        height     : float,
        startAngle : float,  # noqa: N803
        spanAngle  : float   # noqa: N803
    ) -> None:
        ...

    def arcTo(self : Self, *args) -> None:
        """Draw arc. Accepts QRectF or (x, y, width, height) coordinates."""
        if len(args) == 3 and isinstance(args[0], QRectF):
            rect = args[0]
            startAngle = args[1]  # noqa: N806
            spanAngle = args[2]   # noqa: N806
        elif len(args) == 6:
            rect = QRectF(
                float(args[0]), float(args[1]),
                float(args[2]), float(args[3])
            )
            startAngle = args[4]  # noqa: N806
            spanAngle = args[5]   # noqa: N806
        else:
            raise TypeError(
                "arcTo() takes (QRectF, startAngle, spanAngle) or "
                "(x, y, width, height, startAngle, spanAngle)"
            )
        p0 = self.currentPosition()
        super().arcTo(rect, startAngle, spanAngle)
        p1 = self.currentPosition()
        self._mid_pos = (p0 + p1) / 2
        self._angle = degrees(atan2(p1.y() - p0.y(), p1.x() - p0.x()))

    @overload
    def arcSpanTo(
        self      : Self,
        pos       : QPointF,
        spanAngle : float   # noqa: N803
    ) -> None:
        ...

    @overload
    def arcSpanTo(
        self      : Self,
        x         : float,
        y         : float,
        spanAngle : float   # noqa: N803
    ) -> None:
        ...

    def arcSpanTo(self : Self, *args) -> None:
        """Draw arc by span angle. Accepts QPointF or (x, y) coordinates."""
        if len(args) == 2 and isinstance(args[0], QPointF):
            pos = args[0]
            spanAngle = args[1]  # noqa: N806
        elif len(args) == 3:
            pos = QPointF(float(args[0]), float(args[1]))
            spanAngle = args[2]  # noqa: N806
        else:
            raise TypeError(
                "arcSpanTo() takes (QPointF, spanAngle) or (x, y, spanAngle)"
            )
        p0 = self.currentPosition()
        spanAngle = max(-180, min(180, spanAngle))  # noqa: N806
        # chord
        x1 = p0.x()
        y1 = p0.y()
        x2 = pos.x()
        y2 = pos.y()
        dx = x2 - x1  # vector x
        dy = y2 - y1  # vector y
        d = sqrt(dx**2 + dy**2)  # length
        if d < 0.001:  # degenerate case
            self.lineTo(pos)
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

    @overload
    def arcSagittaTo(
        self    : Self,
        pos     : QPointF,
        sagitta : float
    ) -> None:
        ...

    @overload
    def arcSagittaTo(
        self    : Self,
        x       : float,
        y       : float,
        sagitta : float
    ) -> None:
        ...

    def arcSagittaTo(self : Self, *args) -> None:
        """Draw arc by sagitta. Accepts QPointF or (x, y) coordinates."""
        if len(args) == 2 and isinstance(args[0], QPointF):
            pos = args[0]
            sagitta = args[1]
        elif len(args) == 3:
            pos = QPointF(float(args[0]), float(args[1]))
            sagitta = args[2]
        else:
            raise TypeError(
                "arcSagittaTo() takes (QPointF, sagitta) or (x, y, sagitta)"
            )
        p0 = self.currentPosition()
        chord_line = QLineF(p0, pos)
        d = chord_line.length()
        # check for degenerate cases
        if d == 0:
            return
        abs_sagitta = abs(sagitta)
        if abs_sagitta < 1e-6:
            self.lineTo(pos)
        # arc circle radius
        r = (abs_sagitta ** 2 + (d / 2) ** 2) / (2 * abs_sagitta)
        # central angle in degrees (always the *smaller* angle, 0°-180°)
        minor_theta = 2 * degrees(asin((d / 2) / r))
        # Switch to major arc if on the far side
        theta = 360 - minor_theta if abs_sagitta > r else minor_theta
        # Apply the side sign – now span angle can be ±0° to ±360°
        spanAngle = copysign(theta, sagitta)  # noqa: N806
        # more chord parameters
        dx = chord_line.dx()  # vector x
        dy = chord_line.dy()  # vector y
        m = (p0 + pos) / 2  # midpoint
        mx = m.x()  # midpoint x
        my = m.y()  # midpoint y
        # perpendicular unit vector
        ux = sign(spanAngle) *  dy / d
        uy = sign(spanAngle) * -dx / d
        # chord midpoint to arc circle center distance
        h = sqrt(r**2 - (d / 2)**2)
        # arc circle center
        cx = mx + (ux * h)
        cy = my + (uy * h)
        # arc circle bounding rect
        rect = QRectF(cx - r, cy - r, 2 * r, 2 * r)
        # calculate start angle
        c1x = p0.x() - cx
        c1y = p0.y() - cy
        startAngle = degrees(atan2(-c1y, c1x))  # noqa: N806
        # store chord angle and arc midpoint
        a = radians(startAngle + (spanAngle / 2))
        self._mid_pos = QPointF(cx + (r * cos(a)), cy - (r * sin(a)))
        self._angle = degrees(atan2(dy, dx))
        # done
        self.arcTo(rect, startAngle, spanAngle)

    def currentMidPos(self : Self) -> QPointF | None:
        """Midpoint of latest line or arc."""
        return self._mid_pos

    def currentAngle(self : Self) -> float | None:
        """Angle of latest line or arc chord."""
        return self._angle
