from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import Qt, QPoint, QRect, QRectF, QTimer
from PyQt6.QtWidgets import QRubberBand, QGraphicsView
from PyQt6.QtGui     import QPainter, QPen, QColor, QPaintEvent

from ..app import logger

from ..core.check import checked


class MarqueeRubberBand(QRubberBand):
    """
    A custom QRubberBand with a marching ants effect.
    """

    DASH_LEN = 4
    INTERVAL = 100

    offset : int
    timer  : QTimer

    @checked
    def __init__(
        self   : Self,
        shape  : QRubberBand.Shape,
        parent : QGraphicsView
    ) -> None:
        super().__init__(shape, parent)
        self.offset = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        if self.isVisible():
            self.timer.start(self.INTERVAL)

    def animate(self : Self) -> None:
        self.offset = (self.offset + 1) % (2 * self.DASH_LEN)
        self.update()

    def paintEvent(self : Self, a0 : QPaintEvent | None) -> None:
        if a0 is None:
            logger().warning("No event")
            return
        painter = QPainter(self)
        rect = self.rect().adjusted(0, 0, -1, -1)
        pen = QPen(QColor(255, 255, 255))
        pen.setWidth(0)
        pen.setStyle(Qt.PenStyle.CustomDashLine)
        pen.setDashPattern([self.DASH_LEN, self.DASH_LEN])
        pen.setDashOffset(self.offset)
        painter.setPen(pen)
        painter.drawRect(rect)
        pen.setColor(QColor(0, 0, 0))
        pen.setDashOffset((self.offset + self.DASH_LEN) % (2 * self.DASH_LEN))
        painter.setPen(pen)
        painter.drawRect(rect)

    def setVisible(self : Self, visible : bool) -> None:
        super().setVisible(visible)
        if visible:
            self.timer.start(100)
        else:
            self.timer.stop()

class Marquee:
    parent      : QGraphicsView
    rubber_band : MarqueeRubberBand
    point1      : QPoint | None

    @checked
    def __init__(self : Self, parent : QGraphicsView) -> None:
        self.parent = parent
        self.rubber_band = MarqueeRubberBand(
            QRubberBand.Shape.Rectangle,
            parent
        )
        self.point1 = QPoint()

    def begin(self : Self, pos : QPoint) -> None:
        self.point1 = pos
        self.rubber_band.setGeometry(pos.x(), pos.y(), 1, 1)
        self.rubber_band.show()

    def resize(self : Self, pos : QPoint) -> None:
        point1 = self.point1
        if point1 is None:
            raise RuntimeError("No point1")
        self.rubber_band.setGeometry(
            QRect(
                point1.x(), point1.y(),
                pos.x() - point1.x(), pos.y() - point1.y()
            ).normalized()
        )

    def end(self : Self, pos : QPoint) -> None:
        point1 = self.point1
        if point1 is None:
            raise RuntimeError("No point1")
        self.rubber_band.setGeometry(
            QRect(
                point1.x(), point1.y(),
                pos.x() - point1.x(), pos.y() - point1.y()
            ).normalized()
        )
        self.rubber_band.hide()
        self.point1 = None

    def rect(self : Self) -> QRectF:
        prect = self.rubber_band.geometry().normalized() # physical coords
        return QRectF(
            self.parent.mapToScene(prect.topLeft()),
            self.parent.mapToScene(prect.bottomRight())
        )
