__all__ = ["BaseRectangle"]

from typing import Self, Optional, overload

from PyQt6.QtCore    import QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem
from PyQt6.QtGui     import QPainter, QPainterPath

from ....core   import logger

from . import CustomGraphicsRectItem, ElementMixin, cmdPlaceElement, \
              EdgeLoc, Edge, AttrSpec, KP, KPDef, LinePref, FillPref

from .property_text import PropertyText


class BaseRectangle(CustomGraphicsRectItem, ElementMixin):
    """Base class for rectangle elements."""

    # class variables
    _ATTR_SPECS_BASIC = ElementMixin._ATTR_SPECS_BASIC + [
        AttrSpec(
            name      = "Width",
            type_name = "float",
            exists    = lambda self: True,
            getter    = lambda self: self.rect().width(),
            setter    = lambda self, value: self.setWidth(value)
        ),
        AttrSpec(
            name      = "Height",
            type_name = "float",
            exists    = lambda self: True,
            getter    = lambda self: self.rect().height(),
            setter    = lambda self, value: self.setHeight(value)
        )
    ]
    _ATTR_SPECS = \
        _ATTR_SPECS_BASIC + \
        ElementMixin._ATTR_SPECS_APPEARANCE_LINE + \
        ElementMixin._ATTR_SPECS_APPEARANCE_FILL
    MIN_SIZE = QSizeF(1.0, 1.0)
    _KEY_POINTS = [KPDef(k, True, False) for k in KP.__iter__()]

    # instance variables
    _rect          : QRectF
    _bounding_rect : QRectF
    _shape         : QPainterPath

    @overload
    def __init__(
        self : Self,
        rect : QRectF
    ) -> None:
        ...

    @overload
    def __init__(
        self : Self,
        pos  : QPointF,
        size : QSizeF
    ) -> None:
        ...

    @overload
    def __init__(
        self : Self,
        p1   : QPointF,
        p2   : QPointF
    ) -> None:
        ...

    @overload
    def __init__(
        self : Self,
        a1   : float | int,
        a2   : float | int,
        a3   : float | int,
        a4   : float | int
    ) -> None:
        ...

    def __init__(
        self : Self,
        a1   : QRectF | QPointF | float = QRectF(),
        a2   : Optional[QSizeF | QPointF | float] = None,
        a3   : Optional[float | int]              = None,
        a4   : Optional[float | int]              = None,
        bare : bool = False
    ) -> None:
        super().__init__()
        self.initElement(line=LinePref(), fill=FillPref(), text=None, bare=bare)
        self._shape = QPainterPath()
        if isinstance(a1, QRectF):
            self.setRect(a1)
        elif isinstance(a1, QPointF) and isinstance(a2, QSizeF):
            self.setRect(a1, a2)
        elif isinstance(a1, QPointF) and isinstance(a2, QPointF):
            self.setPoints(a1, a2)
        elif isinstance(a1, (float, int)) and isinstance(a2, (float, int)) \
              and isinstance(a3, (float, int)) and isinstance(a4, (float, int)):
            self.setRect(a1, a2, a3, a4)
        else:
            logger.error(f"Invalid arguments: expected (x, y, w, h), (pos, size), or (rect); got {a1}, {a2}, {a3}, {a4}")

    def setRect(
        self       : Self,
        rect_or_ax : Optional[QRectF | float | int] = None,
        ay         : Optional[float | int]          = None,
        w          : Optional[float | int]          = None,
        h          : Optional[float | int]          = None
    ) -> None:
        # TODO handle minimum size
        if isinstance(rect_or_ax, QRectF):
            super().setRect(rect_or_ax)
        else:
            super().setRect(rect_or_ax, ay, w, h)
        self._rect = self.rect()
        w = self.appearance.line.pen.widthF()
        self._bounding_rect = self._rect.adjusted(-w/2, -w/2, w/2, w/2)
        self._shape.clear()
        self._shape.addRect(self._bounding_rect)
        self._kpm.updatePositions()
        for item in self.childItems(): # TODO change to use signal
            if isinstance(item, PropertyText):
                item.refresh()
        self._esm.sizeChanged.emit()

    def boundingRect(self : Self) -> QRectF:
        return self._bounding_rect

    def shape(self : Self) -> QPainterPath:
        return self._shape

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        painter.setPen(self.appearance.line.pen)
        painter.setBrush(self.appearance.fill.brush)
        painter.drawRect(self._rect)

    def KPRect(self : Self) -> QRectF:
        return self._rect

    def setKPVisible(self : Self, visible : bool) -> None:
        self._kpm.setVisible(visible)

    def setSize(self : Self, size : QSizeF) -> None:
        self.setRect(0, 0, size.width(), size.height())

    def setWidth(self : Self, width : float) -> None:
        rect = self.rect()
        rect.setWidth(width)
        self.setRect(rect)

    def setHeight(self : Self, height : float) -> None:
        rect = self.rect()
        rect.setHeight(height)
        self.setRect(rect)

    def setPosSize(self : Self, pos : QPointF, size : QSizeF) -> None:
        self.setPos(pos)
        size.setWidth(max(size.width(), self.MIN_SIZE.width()))
        size.setHeight(max(size.height(), self.MIN_SIZE.height()))
        self.setRect(0, 0, size.width(), size.height())

    @overload
    def setPoints(
        self     : Self,
        p1       : QPointF,
        p2       : QPointF
    ) -> None:
        ...

    @overload
    def setPoints(
        self     : Self,
        x1       : float | int,
        y1       : float | int,
        x2       : float | int,
        y2       : float | int
    ) -> None:
        ...

    def setPoints(
        self     : Self,
        p1_or_x1 : QPointF | float | int,
        p2_or_y1 : QPointF | float | int,
        x2       : Optional[float | int] = None,
        y2       : Optional[float | int] = None
    ) -> None:
        if isinstance(p1_or_x1, QPointF) and isinstance(p2_or_y1, QPointF) \
             and x2 is None and y2 is None:
            p1, p2 = p1_or_x1, p2_or_y1
        elif isinstance(p1_or_x1, float | int) \
             and isinstance(p2_or_y1, float | int) \
             and isinstance(x2, float | int) \
             and isinstance(y2, float | int):
            p1, p2 = QPointF(p1_or_x1, p2_or_y1), QPointF(x2, y2)
        else:
            logger.error(f"Invalid arguments: expected (p1, p2) or (x1, y1, x2, y2); got {p1_or_x1}, {p2_or_y1}, {x2}, {y2}")
            return
        rect = QRectF(p1, p2).normalized()
        self.setPosSize(rect.topLeft(), rect.size())

    def setPosSizeOrP2(
        self       : Self,
        pos        : QPointF,
        size_or_p2 : QSizeF | QPointF
    ) -> None:
        if isinstance(size_or_p2, QSizeF):
            self.setPosSize(pos, size_or_p2)
        else:
            self.setPoints(pos, size_or_p2)

    def getPoints(self : Self) -> tuple[QPointF, QPointF]:
        return self.pos(), self.pos() + self.rect().bottomRight()

    def moveKeyPoint(self : Self, kp : KP, delta : QPointF) -> None:
        p1, p2 = self.getPoints()
        d = delta
        match kp:
            case KP.TOP_LEFT:
                self.setPoints(p1 + d, p2)
            case KP.TOP_CENTER:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x(), p2.y())
            case KP.TOP_RIGHT:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x() + d.x(), p2.y())
            case KP.CENTER_LEFT:
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y())
            case KP.CENTER:
                self.setPos(self.pos() + d)
            case KP.CENTER_RIGHT:
                self.setPoints(p1.x(), p1.y(), p2.x() + d.x(), p2.y())
            case KP.BOTTOM_LEFT:
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y() + d.y())
            case KP.BOTTOM_CENTER:
                self.setPoints(p1.x(), p1.y(), p2.x(), p2.y() + d.y())
            case KP.BOTTOM_RIGHT:
                self.setPoints(p1, p2 + d)
            case _:
                raise ValueError(f"Invalid key point: {kp}")

    @overload
    @classmethod
    def createOrUpdate(
        cls   : Self,
        rect  : QRectF,
        *,
        inst  : Optional[Self] = None
    ) -> "BaseRectangle":
        ...

    @overload
    @classmethod
    def createOrUpdate(
        cls  : Self,
        pos  : QPointF,
        size : QSizeF,
        *,
        inst : Optional[Self] = None
    ) -> "BaseRectangle":
        ...

    @overload
    @classmethod
    def createOrUpdate(
        cls  : Self,
        p1   : QPointF,
        p2   : QPointF,
        *,
        inst : Optional[Self] = None
    ) -> "BaseRectangle":
        ...

    @overload
    @classmethod
    def createOrUpdate(
        cls  : Self,
        ax   : float | int,
        ay   : float | int,
        w    : float | int,
        h    : float | int,
        *,
        inst : Optional[Self] = None
    ) -> "BaseRectangle":
        ...

    @classmethod
    def createOrUpdate(
        cls  : Self,
        a1   : QRectF | QPointF | float | int,
        a2   : Optional[QSizeF | QPointF | float | int] = None,
        a3   : Optional[float | int] = None,
        a4   : Optional[float | int] = None,
        *,
        inst : Optional[Self] = None
    ) -> "BaseRectangle":
        inst = cls() if inst is None else inst
        if isinstance(a1, QRectF) and a2 is None and a3 is None and a4 is None:
            inst.setRect(a1)
        elif isinstance(a1, QPointF) and isinstance(a2, QSizeF) \
             and a3 is None and a4 is None:
            inst.setPosSize(a1, a2)
        elif isinstance(a1, QPointF) and isinstance(a2, QPointF) \
             and a3 is None and a4 is None:
            inst.setPoints(a1, a2)
        elif isinstance(a1, QPointF) and a2 is None \
             and a3 is None and a4 is None:
            inst.setPosSize(a1, cls.MIN_SIZE)
        elif isinstance(a1, float | int) and isinstance(a2, float | int) \
             and isinstance(a3, float | int) and isinstance(a4, float | int):
            inst.setRect(a1, a2, a3, a4)
        else:
            logger.error(f"Invalid arguments: expected (rect), (pos, size), (p1, p2), or (x, y, w, h); got {a1}, {a2}, {a3}, {a4}")
            inst = None
        return inst

    def clone(self : Self) -> Self:
        """Create a clone of this rectangle with a new UUID."""
        clone = super().clone()
        # Copy rectangle-specific properties
        clone.setRect(self.rect())
        return clone

class cmdPlaceBaseRectangle(cmdPlaceElement):
    pass

class BaseRectWithPins(BaseRectangle):
    def getEdgeLoc(self : Self, pos : QPointF) -> EdgeLoc:
        centre_pos = self._rect.center() # always +ve (offset from top left)
        centre_lpos = self.pos() + centre_pos
        # special case: centre
        if pos == centre_lpos:
            return EdgeLoc(Edge.LEFT, half_h)
        size = self._rect.size()
        w = size.width(); h = size.height()
        half_w = w / 2; half_h = h / 2
        offset = pos - centre_lpos
        dx = offset.x(); dy = offset.y()
        # special case: zero width or height => capped linear distance
        if size.width() == 0 and size.height() != 0:
            edge = Edge.LEFT if dx <= 0 else Edge.RIGHT
            distance = min(max(half_h + dy, 0), h)
            return EdgeLoc(edge, distance)
        elif size.height() == 0 and size.width() != 0:
            edge = Edge.TOP if dy <= 0 else Edge.BOTTOM
            distance = min(max(half_w + dx, 0), w)
            return EdgeLoc(edge, distance)
        # special case: zero size
        if size == QSizeF(0, 0):
            if abs(dx) >= abs(dy):
                edge = Edge.LEFT if dx <= 0 else Edge.RIGHT
            else:
                edge = Edge.TOP if dy <= 0 else Edge.BOTTOM
            return EdgeLoc(edge, 0)
        # get edge (quadrant)
        print("dx", dx, "dy", dy, "w", w, "h", h)
        if (h >= w):  # true for tall or square:
            is_vertical = (abs(dx / dy) >= abs(w / h))
        else:  # wide: flip for = case
            is_vertical = (abs(dx / dy) > abs(w / h))
        if is_vertical:
            edge = Edge.LEFT if dx < 0 else Edge.RIGHT
        else:
            edge = Edge.TOP if dy < 0 else Edge.BOTTOM
        # get distance
        if edge in [Edge.LEFT, Edge.RIGHT]:
            scaled_dy = dy * abs(half_w/ dx)
            distance = half_h + scaled_dy
        elif edge in [Edge.TOP, Edge.BOTTOM]:
            scaled_dx = dx * abs(half_h / dy)
            distance = half_w + scaled_dx
        return EdgeLoc(edge, distance)

    def getEdgeLocPos(self : Self, loc : EdgeLoc) -> QPointF:
        match loc.edge:
            case Edge.LEFT:
                return QPointF(0, loc.distance)
            case Edge.RIGHT:
                return QPointF(self.rect().width(), loc.distance)
            case Edge.TOP:
                return QPointF(loc.distance, 0)
            case Edge.BOTTOM:
                return QPointF(loc.distance, self.rect().height())
            case _:
                raise ValueError(f"Invalid edge: {loc.edge}")

class cmdPlaceBaseRectWithPins(cmdPlaceBaseRectangle):
    element : BaseRectWithPins
