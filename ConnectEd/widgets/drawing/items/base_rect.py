__all__ = ["BaseRectangle"]

from typing import Self, Optional, overload

from PyQt6.QtCore    import Qt, QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QGraphicsRectItem, \
                            QWidget, QStyleOptionGraphicsItem, QStyle
from PyQt6.QtGui     import QPainter, QPainterPath, QPainterPathStroker

from ....core   import logger

from ..properties import PropertySpec

from ..properties import PropertySpec, PropertiesMixin

from . import KPLoc, \
              ElementMixin, \
              ElementBoundShapeMixin, \
              ElementPosMixin, \
              ElementRectKeypointsMixin, \
              ElementLineMixin, \
              ElementFillMixin, \
              ElementChangeMixin, \
              ElementCloneMixin, \
              ElementXmlMixin, \
              ElementMenuMixin, \
              cmdPlaceElement

from .... import hub


class BaseRectangle(
    ElementMixin,
    ElementBoundShapeMixin,
    ElementPosMixin,
    ElementRectKeypointsMixin,
    ElementLineMixin,
    ElementFillMixin,
    ElementChangeMixin,
    ElementCloneMixin,
    ElementXmlMixin,
    ElementMenuMixin,
    PropertiesMixin,
    QGraphicsRectItem
):
    """Base class for rectangle elements."""

    # class variables
    _PROPERTY_SPECS = \
        ElementPosMixin._PROPERTY_SPECS_POS | \
        {
            "Width" : PropertySpec(
                type_name = "float",
                exists    = lambda self: True,
                getter    = lambda self: self.rect().width(),
                setter    = lambda self, value: self.setWidth(value)
            ),
            "Height" : PropertySpec(
                type_name = "float",
                exists    = lambda self: True,
                getter    = lambda self: self.rect().height(),
                setter    = lambda self, value: self.setHeight(value)
            )
        } | \
        ElementLineMixin._PROPERTY_SPECS_LINE | \
        ElementFillMixin._PROPERTY_SPECS_FILL
    _MIN_SIZE = QSizeF(1.0, 1.0)

    # instance variables
    _rect : QRectF  # cached rectangle

    def __init__(self : Self, bare : bool = False) -> None:
        super().__init__()
        self.initElement(bare=bare)

    def onSizeChange(self : Self) -> None:
        self.prepareGeometryChange() # because boundaryRect and shape may change
        pen_width = self.line.pen.widthF()
        tolerance = hub.settings.get("display/select/tolerance")
        stroke_width = pen_width + (2 * tolerance)
        rect_path = QPainterPath()
        rect_path.addRect(self._rect)
        stroker = QPainterPathStroker()
        stroker.setWidth(stroke_width)
        stroker.setCapStyle(Qt.PenCapStyle.SquareCap)
        stroker.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        stroker_path = stroker.createStroke(rect_path)
        self._brect = stroker_path.boundingRect()
        if self.fill.brush.style() != Qt.BrushStyle.NoBrush:
            self._hshape = rect_path.united(stroker_path)
        else:
            self._hshape = stroker_path
        self.updateKeypoints()

    def getMenuItems(self : Self) -> list[str]:
        return ["Appearance..."]

    @overload
    def setRect(
        self : Self,
        ax : float | int,
        ay : float | int,
        w : float | int,
        h : float | int
    ) -> None:
        ...

    @overload
    def setRect(
        self : Self,
        rect : QRectF
    ) -> None:
        ...

    def setRect(
        self       : Self,
        rect_or_ax : float | int,
        ay         : float | int = None,
        w          : float | int = None,
        h          : float | int = None
    ) -> None:
        if isinstance(rect_or_ax, QRectF):
            super().setRect(rect_or_ax)
        else:
            super().setRect(rect_or_ax, ay, w, h)
        self._kprect = self._rect = self.rect()
        self.onSizeChange()

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, option, widget)

    def setPosSize(self : Self, pos : QPointF, size : QSizeF) -> None:
        self.setPos(pos)
        size.setWidth(max(size.width(), self._MIN_SIZE.width()))
        size.setHeight(max(size.height(), self._MIN_SIZE.height()))
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

    def moveKeypoint(self : Self, kp : KPLoc, delta : QPointF) -> None:
        p1, p2 = self.getPoints()
        d = delta
        match kp:
            case KPLoc.TOP_LEFT:
                self.setPoints(p1 + d, p2)
            case KPLoc.TOP_CENTER:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x(), p2.y())
            case KPLoc.TOP_RIGHT:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x() + d.x(), p2.y())
            case KPLoc.CENTER_LEFT:
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y())
            case KPLoc.CENTER:
                self.setPos(self.pos() + d)
            case KPLoc.CENTER_RIGHT:
                self.setPoints(p1.x(), p1.y(), p2.x() + d.x(), p2.y())
            case KPLoc.BOTTOM_LEFT:
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y() + d.y())
            case KPLoc.BOTTOM_CENTER:
                self.setPoints(p1.x(), p1.y(), p2.x(), p2.y() + d.y())
            case KPLoc.BOTTOM_RIGHT:
                self.setPoints(p1, p2 + d)
            case _:
                raise ValueError(f"Invalid key point: {kp}")

    @classmethod
    def createOrUpdate(
        cls  : Self,
        *,
        pos  : Optional[QPointF]     = None,
        size : Optional[QSizeF]      = None,
        p1   : Optional[QPointF]     = None,
        p2   : Optional[QPointF]     = None,
        x1   : Optional[float | int] = None,
        y1   : Optional[float | int] = None,
        x2   : Optional[float | int] = None,
        y2   : Optional[float | int] = None,
        inst : Optional[Self] = None
    ) -> "BaseRectangle":
        inst = cls() if inst is None else inst
        if pos is not None:
            inst.setPos(pos)
        if size is not None:
            inst.setSize(size)
        if p1 is not None and p2 is not None:
            inst.setPoints(p1, p2)
        if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
            inst.setRect(x1, y1, x2 - x1, y2 - y1)
        return inst

    def clone(self : Self) -> Self:
        """Create a clone of this rectangle with a new UUID."""
        clone = super().clone()
        # Copy rectangle-specific properties
        clone.setRect(self.rect())
        return clone

class cmdPlaceBaseRectangle(cmdPlaceElement):
    pass
