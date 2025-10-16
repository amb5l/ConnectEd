from typing import Self, overload

from PyQt6.QtCore    import Qt, QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QGraphicsRectItem, \
                            QWidget, QStyleOptionGraphicsItem, QStyle
from PyQt6.QtGui     import QPainter, QPainterPath, QPainterPathStroker

from ....app import settings

from ..properties import PropertySpec, PropertiesMixin

from .mixin        import ElementMixin
from .mixin.bound  import ElementBoundMixin
from .mixin.shape  import ElementShapeMixin
from .mixin.pos    import ElementPosMixin
from .mixin.anchor import ElementRectAnchorPointsMixin
from .mixin.line   import ElementLineMixin
from .mixin.fill   import ElementFillMixin
from .mixin.change import ElementChangeMixin
from .mixin.clone  import ElementCloneMixin
from .mixin.xml    import ElementXmlMixin
from .mixin.menu   import ElementMenuMixin


class BaseRectangle(
    ElementMixin,
    ElementBoundMixin,
    ElementShapeMixin,
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

    # class attributes
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
    _ap_rect : QRectF  # anchor point rectangle

    @overload
    def __init__(
        self : Self,
        p1   : QPointF | None = None,
        p2   : QPointF | None = None,
        bare : bool = False
    ) -> None:
        ...

    @overload
    def __init__(
        self : Self,
        pos  : QPointF | None = None,
        size : QSizeF | None = None,
        bare : bool = False
    ) -> None:
        ...

    def __init__(
        self       : Self,
        p1_or_pos  : QPointF | None = None,
        p2_or_size : QPointF | None = None,
        bare       : bool = False
    ) -> None:
        super().__init__()
        self._ap_rect = QRectF()
        self.initElement(bare=bare)
        if p1_or_pos is None:
            p1_or_pos = QPointF()
        if p2_or_size is None:
            p2_or_size = QSizeF(0, 0)
        if isinstance(p2_or_size, QSizeF):
            p2_or_size = QPointF(
                p1_or_pos.x() + p2_or_size.width(),
                p1_or_pos.y() + p2_or_size.height()
            )
        self.setPoints(p1_or_pos, p2_or_size)
        self.onGeometryChange()

    def onGeometryChange(self : Self) -> None:
        self.prepareGeometryChange()
        pen_width = self.a.line.pen.widthF()
        tolerance = settings().get("display/select/tolerance")
        stroke_width = pen_width + (2 * tolerance)
        rect_path = QPainterPath()
        rect_path.addRect(self.rect())
        stroker = QPainterPathStroker()
        stroker.setWidth(stroke_width)
        stroker.setCapStyle(Qt.PenCapStyle.SquareCap)
        stroker.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        stroker_path = stroker.createStroke(rect_path)
        self._brect = stroker_path.boundingRect()
        if self.a.fill.brush.style() != Qt.BrushStyle.NoBrush:
            self._hshape = rect_path.united(stroker_path)
        else:
            self._hshape = stroker_path
        self.updateAnchorPoints()

    def getMenuItems(self : Self) -> list[str]:
        return ["Appearance...", "Properties..."]

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
        self._ap_rect = self.rect()
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
        rect = self.rect()
        rect.setWidth(width)
        self.setRect(rect)

    def setHeight(self : Self, height : float | int) -> None:
        rect = self.rect()
        rect.setHeight(height)
        self.setRect(rect)

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
        x2    : float | int | None = None,
        y2    : float | int | None = None
    ) -> None:
        if x2 is None or y2 is None:
            x1 = p1_x1.x()
            y1 = p1_x1.y()
            x2 = p2_y1.x()
            y2 = p2_y1.y()
        else:
            x1 = p1_x1
            y1 = p2_y1
        final_pos = QPointF(
            x1 if x1 < x2 else x2,
            y1 if y1 < y2 else y2,
        )
        self.setPos(final_pos)
        w = max(abs(x2-x1), self._MIN_SIZE.width())
        h = max(abs(y2-y1), self._MIN_SIZE.height())
        rect = self.rect()
        rect.setSize(QSizeF(w, h))
        self.setRect(rect)

    def moveAnchorPointBy(self : Self, name : str, delta : QPointF) -> None:
        p1 = self.pos()
        p2 = p1 + self.rect().bottomRight()
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
