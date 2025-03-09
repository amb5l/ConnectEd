from typing import ClassVar, Optional

from PyQt6.QtCore    import QRectF
from PyQt6.QtWidgets import QStyleOptionGraphicsItem, QWidget
from PyQt6.QtGui     import QPainter, QPen

from ..core import Z_TEMPLATE, settings
from .      import Element, LineSpec
from .sheet import Sheet

class Border(Element):
    Z      : ClassVar[int] = Z_TEMPLATE
    sheet  : Sheet
    margin : float
    line   : LineSpec

    def __init__(
        self   : 'Border',
        sheet  : Sheet,
        margin : Optional[float] = None,
        line   : Optional[LineSpec] = None
    ) -> None:
        super().__init__()
        self.sheet  = sheet
        if margin is None:
            margin = settings.defaults.margin
        self.margin = margin
        self.line   = line

    def boundingRect(self) -> QRectF:
        if self.margin:
            w = self.line.width if self.line is not None else \
                settings.prefs.display.elements.border.width
            rect  = self.sheet.rect.adjusted(
                self.margin, self.margin, -self.margin, -self.margin
            )
            return rect.adjusted(-w/2, -w/2, w/2, w/2)
        else:
            return self.sheet.rect

    def paint(
        self    : 'Border',
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        if self.margin: # zero margin means no border
            rect  = self.sheet.rect.adjusted(
                self.margin, self.margin, -self.margin, -self.margin
            )
            painter.setPen(QPen(
                settings.theme.border,
                settings.prefs.display.elements.border.width,
                settings.prefs.display.elements.border.style
            ))
            painter.drawRect(rect)
