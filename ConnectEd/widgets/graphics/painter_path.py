from typing import Self, TypeGuard, overload
from math   import copysign, sqrt, degrees, radians, sin, cos, asin, atan2

from PyQt6.QtCore import QPointF, QLineF, QRectF
from PyQt6.QtGui  import QPainterPath

from ...core.check import checked
from ...core.utils import sign


def _isNum(value : object) -> TypeGuard[int | float]:
    """True for int/float, excluding bool (bool is a subclass of int)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


class PainterPath(QPainterPath):
    """QPainterPath with enhanced arc and grip support."""

    # instance attributes
    _mid_pos : QPointF  # latest line/arc midpoint
    _angle   : float    # angle of latest line/arc chord

    @checked
    def __init__(self : Self) -> None:
        super().__init__()

    @overload
    def lineTo(self : Self, p : QPointF) -> None:
        ...

    @overload
    def lineTo(self : Self, x : float, y : float) -> None:
        ...

    @checked
    def lineTo(  # pyright: ignore[reportInconsistentOverload]
        self   : Self,
        p_or_x : QPointF | float,
        y      : float | None = None
    ) -> None:
        """Override to store midpoint. Accepts QPointF or (x, y) coordinates."""
        if isinstance(p_or_x, QPointF):
            pos = p_or_x
        elif _isNum(p_or_x) and _isNum(y):
            pos = QPointF(float(p_or_x), float(y))
        else:
            raise TypeError("lineTo() takes either QPointF or (x, y) coordinates")
        p0 = self.currentPosition()
        super().lineTo(pos)
        self._mid_pos = (pos + p0) / 2
        self._angle = degrees(atan2(pos.y() - p0.y(), pos.x() - p0.x()))

    @overload
    def arcTo(
        self       : Self,
        a0         : QRectF,
        a1         : float,   # start angle
        a2         : float    # span angle
    ) -> None:
        ...

    @overload
    def arcTo(
        self : Self,
        a0   : float,  # x
        a1   : float,  # y
        a2   : float,  # width
        a3   : float,  # height
        a4   : float,  # start angle
        a5   : float   # span angle
    ) -> None:
        ...

    @checked
    def arcTo(  # pyright: ignore[reportIncompatibleMethodOverride]
        self : Self,
        a0   : QRectF | float,       # rect or x
        a1   : float,                # start angle or y
        a2   : float,                # span angle or width
        a3   : float | None = None,  # None or height
        a4   : float | None = None,  # None or start angle
        a5   : float | None = None   # None or span angle
    ) -> None:
        """Draw arc. Accepts QRectF or (x, y, width, height) coordinates."""
        if isinstance(a0, QRectF) and _isNum(a1) and _isNum(a2):
            rect = a0
            start_angle = float(a1)
            span_angle = float(a2)
        elif _isNum(a0) and _isNum(a1) and _isNum(a2) \
         and _isNum(a3) and _isNum(a4) and _isNum(a5):
            rect = QRectF(float(a0), float(a1), float(a2), float(a3))
            start_angle = float(a4)
            span_angle = float(a5)
        else:
            raise TypeError(
                "arcTo() takes (QRectF, startAngle, spanAngle) or "
                "(x, y, width, height, startAngle, spanAngle)"
            )
        p0 = self.currentPosition()
        super().arcTo(rect, start_angle, span_angle)
        p1 = self.currentPosition()
        self._mid_pos = (p0 + p1) / 2
        self._angle = degrees(atan2(p1.y() - p0.y(), p1.x() - p0.x()))

    @overload
    def arcSpanTo(
        self : Self,
        a0   : QPointF,  # pos
        a1   : float     # span angle
    ) -> None:
        ...

    @overload
    def arcSpanTo(
        self : Self,
        a0   : float,  # x
        a1   : float,  # y
        a2   : float   # span angle
    ) -> None:
        ...

    @checked
    def arcSpanTo(
        self : Self,
        a0   : QPointF | float,     # pos or x
        a1   : float,               # span angle or y
        a2   : float | None = None  # None or span angle
    ) -> None:
        """Draw arc by span angle. Accepts QPointF or (x, y) coordinates."""
        if isinstance(a0, QPointF) and _isNum(a1):
            pos = a0
            span_angle = float(a1)
        elif _isNum(a0) and _isNum(a1) and _isNum(a2):
            pos = QPointF(float(a0), float(a1))
            span_angle = float(a2)
        else:
            raise TypeError(
                "arcSpanTo() takes (QPointF, spanAngle) or (x, y, spanAngle)"
            )
        p0 = self.currentPosition()
        span_angle = max(-180.0, min(180.0, span_angle))
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
            return
        mx = (x1 + x2) / 2  # midpoint x
        my = (y1 + y2) / 2  # midpoint y
        # arc circle radius
        r = d / (2 * sin(radians(abs(span_angle) / 2)))
        # chord midpoint to arc circle center distance
        h = sqrt(r**2 - (d / 2)**2)
        # perpendicular unit vector
        ux = sign(span_angle) *  dy / d
        uy = sign(span_angle) * -dx / d
        # arc circle center
        cx = mx + (ux * h)
        cy = my + (uy * h)
        # arc circle bounding rect
        rect = QRectF(cx - r, cy - r, 2 * r, 2 * r)
        # calculate start angle
        c1x = x1 - cx
        c1y = y1 - cy
        start_angle = degrees(atan2(-c1y, c1x))
        # store chord angle and arc midpoint
        a = radians(start_angle + (span_angle / 2))
        self._mid_pos = QPointF(cx + (r * cos(a)), cy - (r * sin(a)))
        self._angle = degrees(atan2(dy, dx))
        return super().arcTo(rect, start_angle, span_angle)

    @overload
    def arcSagittaTo(
        self : Self,
        a0   : QPointF,  # pos
        a1   : float     # sagitta
    ) -> None:
        ...

    @overload
    def arcSagittaTo(
        self : Self,
        a0   : float,  # X
        a1   : float,  # Y
        a2   : float   # Sagitta
    ) -> None:
        ...

    @checked
    def arcSagittaTo(
        self : Self,
        a0   : QPointF | float,     # pos or x
        a1   : float,               # sagitta or y
        a2   : float | None = None  # None or sagitta
    ) -> None:
        """Draw arc by sagitta. Accepts QPointF or (x, y) coordinates."""
        if isinstance(a0, QPointF) and _isNum(a1):
            pos = a0
            sagitta = float(a1)
        elif _isNum(a0) and _isNum(a1) and _isNum(a2):
            pos = QPointF(float(a0), float(a1))
            sagitta = float(a2)
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
            return
        # arc circle radius
        r = (abs_sagitta ** 2 + (d / 2) ** 2) / (2 * abs_sagitta)
        # central angle in degrees (always the *smaller* angle, 0°-180°)
        minor_theta = 2 * degrees(asin((d / 2) / r))
        # Switch to major arc if on the far side
        theta = 360 - minor_theta if abs_sagitta > r else minor_theta
        # Apply the side sign – now span angle can be ±0° to ±360°
        span_angle = copysign(theta, sagitta)
        # more chord parameters
        dx = chord_line.dx()  # vector x
        dy = chord_line.dy()  # vector y
        m = (p0 + pos) / 2  # midpoint
        mx = m.x()  # midpoint x
        my = m.y()  # midpoint y
        # perpendicular unit vector
        ux = sign(span_angle) *  dy / d
        uy = sign(span_angle) * -dx / d
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
        start_angle = degrees(atan2(-c1y, c1x))
        # store chord angle and arc midpoint
        a = radians(start_angle + (span_angle / 2))
        self._mid_pos = QPointF(cx + (r * cos(a)), cy - (r * sin(a)))
        self._angle = degrees(atan2(dy, dx))
        # done
        self.arcTo(rect, start_angle, span_angle)

    def currentMidPos(self : Self) -> QPointF:
        """Midpoint of latest line or arc."""
        return self._mid_pos

    def currentAngle(self : Self) -> float:
        """Angle of latest line or arc chord."""
        return self._angle
