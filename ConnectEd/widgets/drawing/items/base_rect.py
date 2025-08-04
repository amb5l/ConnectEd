__all__ = ["BaseRectangle"]

from typing import Self, Optional, overload

from PyQt6.QtCore    import Qt, QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QGraphicsRectItem, \
                            QWidget, QStyleOptionGraphicsItem, QStyle
from PyQt6.QtGui     import QPainter, QPainterPath, QPainterPathStroker

from ..properties import PropertySpec, PropertiesMixin

from . import APType, \
              ElementMixin, \
              ElementBoundShapeMixin, \
              ElementPosMixin, \
              ElementRectAnchorPointsMixin, \
              ElementLineMixin, \
              ElementFillMixin, \
              ElementChangeMixin, \
              ElementCloneMixin, \
              ElementXmlMixin, \
              ElementMenuMixin

from .... import hub


class BaseRectangle(
    ElementMixin,
    ElementBoundShapeMixin,
    ElementPosMixin,
    ElementRectAnchorPointsMixin,
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
    _AP_TYPES = { k : APType.Mover if k == "Center" else APType.Resizer \
            for k in ElementRectAnchorPointsMixin._ANCHOR_POINTS.keys() }
    _PROPERTY_SPECS = \
        ElementPosMixin._PROPERTY_SPECS_POS | \
        {
            "Width" : PropertySpec(
                type_name = "float",
                getter    = lambda self: self.rect().width(),
                setter    = lambda self, value: self.setWidth(value)
            ),
            "Height" : PropertySpec(
                type_name = "float",
                getter    = lambda self: self.rect().height(),
                setter    = lambda self, value: self.setHeight(value)
            )
        } | \
        ElementLineMixin._PROPERTY_SPECS_LINE | \
        ElementFillMixin._PROPERTY_SPECS_FILL
    _MIN_SIZE = QSizeF(1.0, 1.0)

    # instance attributes
    _rect : QRectF  # cached rectangle
    _p1   : QPointF # first corner

    def __init__(
        self : Self,
        p1   : Optional[QPointF] = None,
        p2   : Optional[QPointF] = None,
        bare : bool = False
    ) -> None:
        super().__init__()
        self.initElement(bare=bare)
        self._rect = QRectF()
        if p1 is None and p2 is None:
            self._p1 = QPointF()
        elif p2 is None:
            self._p1 = p1
            self.setPos(p1)
        else:
            self._p1 = p1
            self.setPoints(p1, p2)

    def onGeometryChange(self : Self) -> None:
        self.prepareGeometryChange()
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
        self._rect = self.rect()
        self.onGeometryChange()

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, option, widget)

    def setWidth(self : Self, width : float | int) -> None:
        self._rect.setWidth(width)
        self.setRect(self._rect)

    def setHeight(self : Self, height : float | int) -> None:
        self._rect.setHeight(height)
        self.setRect(self._rect)

    @overload
    def setPoints(
        self : Self,
        p1   : QPointF,
        p2   : QPointF
    ) -> None:
        ...

    @overload
    def setPoints(
        self : Self,
        x1   : float | int,
        y1   : float | int,
        x2   : float | int,
        y2   : float | int
    ) -> None:
        ...

    def setPoints(
        self : Self,
        p1_x1 : QPointF | float | int,
        p2_y1 : QPointF | float | int,
        x2    : Optional[float | int] = None,
        y2    : Optional[float | int] = None
    ) -> None:
        if x2 is None or y2 is None:
            x1 = p1_x1.x()
            y1 = p1_x1.y()
            x2 = p2_y1.x()
            y2 = p2_y1.y()
        else:
            x1 = p1_x1
            y1 = p2_y1
        self.setPos(QPointF(
            x1 if x1 < x2 else x2,
            y1 if y1 < y2 else y2,
        ))
        w = max(abs(x2-x1), self._MIN_SIZE.width())
        h = max(abs(y2-y1), self._MIN_SIZE.height())
        self._rect.setSize(QSizeF(w, h))
        self.setRect(self._rect)

    def setP2(self : Self, p2 : QPointF) -> None:
        self.setPoints(
            self._p1.x(),
            self._p1.y(),
            p2.x(),
            p2.y()
        )
        self.setRect(self._rect)

    def moveAnchorPointBy(self : Self, name : str, delta : QPointF) -> None:
        p1 = self.pos()
        p2 = p1 + self._rect.bottomRight()
        d = delta
        match name:
            case "Top Left":
                self.setPoints(p1 + d, p2)
            case "Top Center":
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x(), p2.y())
            case "Top Right":
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x() + d.x(), p2.y())
            case "Center Left":
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y())
            case "Center":
                self.setPos(self.pos() + d)
            case "Center Right":
                self.setPoints(p1.x(), p1.y(), p2.x() + d.x(), p2.y())
            case "Bottom Left":
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y() + d.y())
            case "Bottom Center":
                self.setPoints(p1.x(), p1.y(), p2.x(), p2.y() + d.y())
            case "Bottom Right":
                self.setPoints(p1, p2 + d)
            case _:
                raise ValueError(f"Invalid anchor point: {name}")
