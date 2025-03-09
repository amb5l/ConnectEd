from typing import ClassVar, Optional

from PyQt6.QtCore    import QRectF, QPointF
from PyQt6.QtGui     import QPainter
from PyQt6.QtWidgets import QStyleOptionGraphicsItem, QWidget

from ..core import Z_DRAWING, settings, Rect2

from . import Element, LineSpec, FillSpec


class Rectangle(Element):
    Z    : ClassVar[int] = Z_DRAWING
    rect : Rect2
    line : LineSpec
    fill : FillSpec

    def __init__(
        self     : 'Rectangle',
        p1       : QPointF,
        p2       : Optional[QPointF] = None,
        line     : Optional[LineSpec] = None,
        fill     : Optional[FillSpec] = None,
        selected : bool = False,
        wip      : bool = False
    ) -> None:
        super().__init__(selected, wip)
        self.rect = Rect2(p1, p2)
        self.line = line
        self.fill = fill

    def setPoint2(self : 'Rectangle', p2 : QPointF) -> None:
        self.rect.setPoint2(p2)

    def boundingRect(self) -> QRectF:
        w = self.line.width if self.line is not None else \
            settings.prefs.display.elements.rectangle.line.width
        margin = w / 2
        return self.rect.adjusted(-margin, -margin, margin, margin)

    def paint(
        self    : 'Rectangle',
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        self.setPenBrush(
            painter,
            settings.prefs.display.elements.rectangle,
            settings.theme.elements.rectangle
        )
        painter.drawRect(self.rect)
