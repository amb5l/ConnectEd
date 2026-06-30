from typing import Self

from PyQt6.QtCore    import Qt, QPoint, QPointF,QRectF
from PyQt6.QtGui     import QColor, QPainter, QPen

from ....app import settings

from ....core.check import checked
from ....core.doc   import DocBinding

from ...window.mdi_area import MdiArea

from ..scenes.symbol import SymbolScene

from .diagram import DiagramView, DiagramSubWindow


class SymbolView(DiagramView):
    # instance attributes
    _pen : QPen

    @checked
    def __init__(self : Self, scene : SymbolScene) -> None:
        super().__init__(scene)
        self.onSettingsChanged()
        settings().changed.connect(self.onSettingsChanged)

    def drawForeground(
        self    : Self,
        painter : QPainter | None,
        rect    : QRectF,
    ) -> None:
        if painter is None:
            return
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


class SymbolSubWindow(DiagramSubWindow):
    @checked
    def __init__(
        self        : Self,
        parent      : MdiArea | None = None,
        doc_binding : DocBinding | None = None,
    ) -> None:
        super().__init__(parent, doc_binding)
