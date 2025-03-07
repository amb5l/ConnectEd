from typing import Optional

from PyQt6.QtCore import QRectF, QPointF

from ..core import settings

from . import Element, LineSpec, FillSpec, PainterContext


class Rectangle(Element):
    point1 : QPointF
    point2 : QPointF
    rect   : QRectF
    line   : LineSpec
    fill   : FillSpec

    def __init__(
        self : 'Rectangle',
        p1   : QPointF,
        p2   : Optional[QPointF] = None,
        line : LineSpec = LineSpec(),
        fill : FillSpec = FillSpec()
    ) -> None:
        self.rect = QRectF()
        self.point1 = QPointF()
        self.point2 = QPointF()
        if p2 is None:
            p2 = p1
        self.setPoints(p1, p2)
        self.line = line
        self.fill = fill

    def setPoints(self : 'Rectangle', p1 : QPointF, p2 : QPointF) -> None:
        self.point1.setX(p1.x()); self.point1.setY(p1.y())
        self.setPoint2(p2)

    def setPoint2(self : 'Rectangle', p2 : QPointF) -> None:
        if p2.x() == self.point1.x():
            p2.setX(self.point1.x()+1)
        if p2.y() == self.point1.y():
            p2.setY(self.point1.y()+1)
        self.point2.setX(p2.x()); self.point2.setY(p2.y())
        self.rect.setCoords(self.point1.x(), self.point1.y(), p2.x(), p2.y())

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
