from PyQt6.QtCore import QRectF, QPointF, QSizeF

from ..core import settings

from . import Element, LineSpec, FillSpec, PainterContext


class Rectangle(Element):
    rect : QRectF
    line : LineSpec
    fill : FillSpec

    def __init__(
        self     : 'Rectangle',
        position : QPointF,
        size     : QSizeF = QSizeF(1, 1),
        line     : LineSpec = LineSpec(),
        fill     : FillSpec = FillSpec()
    ) -> None:
        self.rect = QRectF(position, size)
        self.line = line
        self.fill = fill

    def setRect(self : 'Rectangle', p1 : QPointF, p2 : QPointF) -> None:
        self.rect.setCoords(p1.x(), p1.y(), p2.x(), p2.y())

    def paint(self, ctx : PainterContext, wip : bool = False) -> None:
        if wip:
            ctx.setFromAttrs(
                self,
                settings.prefs.display.elements.wip,
                settings.theme.elements.wip
            )
        else:
            ctx.setFromAttrs(
                self,
                settings.prefs.display.elements.rectangle,
                settings.theme.elements.rectangle
            )
            ctx.setAlpha(settings.prefs.display.elements.alpha)
        ctx.painter.drawRect(self.rect)
