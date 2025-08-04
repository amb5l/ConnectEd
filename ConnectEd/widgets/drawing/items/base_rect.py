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

    def __init__(self : Self, bare : bool = False) -> None:
        super().__init__()
        self._rect = self.rect()
        self.initElement(bare=bare)

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

    def setPoints(
        self : Self,
        x1   : float | int,
        y1   : float | int,
        x2   : float | int,
        y2   : float | int
    ) -> None:
        self.setPos(x1, y1)
        self._rect.setCoords(0, 0, x2-x1, y2-y1)
        self.setRect(self._rect)

    def moveAnchorPoint(self : Self, name : str, delta : QPointF) -> None:
        p1 = self.pos()
        p2 = p1 + self._rect.bottomRight()
        d = delta
        match name:
            case "Top Left":
                self.setPoints(p1.x() + d.x(), p1.y() + d.y(), p2.x(), p2.y())
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
                self.setPoints(p1.x(), p1.y(), p2.x() + d.x(), p2.y() + d.y())
            case _:
                raise ValueError(f"Invalid anchor point: {name}")

    @classmethod
    def createOrUpdate(
        cls  : Self,
        *,
        p1   : QPointF,
        p2   : Optional[QPointF] = None,
        inst : Optional[Self]    = None
    ) -> "BaseRectangle":
        inst = cls() if inst is None else inst
        if p2 is None:
            inst.setPos(p1)
        else:
            inst.setPoints(p1.x(), p1.y(), p2.x(), p2.y())
        return inst
