from typing import Self

from PyQt6.QtCore    import Qt, QEvent, QPoint, QPointF,QRectF
from PyQt6.QtWidgets import QMdiArea
from PyQt6.QtGui     import QColor, QPainter, QPen

from ....app import settings

from ....core.check import checked

from ..scenes.symbol import SymbolScene

from .drawing import DrawingView, DrawingSubWindow


class SymbolView(DrawingView):
    # instance attributes
    _pen : QPen

    @checked
    def __init__(self : Self, scene : SymbolScene) -> None:
        super().__init__(scene)
        self.onSettingsChanged()
        settings().changed.connect(self.onSettingsChanged)

    def showEvent(self : Self, event : QEvent) -> None:
        super().showEvent(event)
        self.viewZoomAll()

    def drawForeground(self : Self, painter : QPainter, rect : QRectF) -> None:
        super().drawForeground(painter, rect)
        painter.save()
        painter.resetTransform()
        origin = self.mapFromScene(QPointF(0, 0))
        painter.setPen(self._pen)
        h = int(settings().get("theme/origin/size") / 2)
        painter.drawLine(origin - QPoint(h, 0), origin + QPoint(h, 0))
        painter.drawLine(origin - QPoint(0, h), origin + QPoint(0, h))
        painter.drawEllipse(origin, h, h)
        painter.restore()

    def onSettingsChanged(self : Self) -> None:
        pen_color : QColor = settings().get("theme/origin/color")
        pen_color.setAlpha(settings().get("display/alpha"))
        self._pen = QPen(pen_color, 1, Qt.PenStyle.SolidLine)


class SymbolSubWindow(DrawingSubWindow):
    @checked
    def __init__(
        self   : Self,
        parent : QMdiArea | None = None
    ) -> None:
        super().__init__(parent)
