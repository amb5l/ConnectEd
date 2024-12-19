from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui  import QPaintEvent, QResizeEvent, QPainter, QPen, QBrush
from typing import TYPE_CHECKING

from settings import prefs, theme

if TYPE_CHECKING:
    from canvas import Canvas

class CanvasEventsPaintMixin:
    def paintEvent(self : 'Canvas', event : QPaintEvent):
        painter = QPainter(self)
        # draw void

        # get extents of visible portion of canvas
        self.visibleRect = self.rect()

        # draw background
        painter.fillRect(self.visibleRect, prefs.draw.theme.background)
        # draw diagram
        if self.diagram.data is None:
            pass
        else:
            painter.scale(self.zoom, self.zoom)
            painter.translate(-self.pan)
            self.diagram.draw(painter, self.alpha)
        # edit state dependant drawing
        if self.State == self.State.SELECT_WIN_1:
            pen = QPen(prefs.draw.theme.selected.line, 0, Qt.PenStyle.DotLine)
            brush = QBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(pen)
            painter.setBrush(brush)
            painter.drawRect(QRectF(self.startPos, self.currentPos))
        # draw grid
        if prefs.display.grid.enable:
            x1 = int( self.gridRect.left()   / prefs.display.grid.x )
            y1 = int( self.gridRect.top()    / prefs.display.grid.y )
            x2 = int( self.gridRect.right()  / prefs.display.grid.x )
            y2 = int( self.gridRect.bottom() / prefs.display.grid.y )
            color = theme.grid
            color.setAlpha(prefs.display.grid.alpha)
            pen = QPen(color, 0, Qt.PenStyle.SolidLine)
            brush = QBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(pen)
            painter.setBrush(brush)
            if prefs.display.grid.dots:
                for x in range(x1, x2+1):
                    for y in range(y1, y2+1):
                        painter.drawPoint(
                            QPointF(x * prefs.edit.grid.x, y * prefs.edit.grid.y)
                        )
            else:
                for x in range(x1, x2+1):
                    painter.drawLine(
                        QPointF(x  * prefs.edit.grid.x, y1 * prefs.edit.grid.y),
                        QPointF(x  * prefs.edit.grid.x, y2 * prefs.edit.grid.y)
                    )
                for y in range(y1, y2+1):
                    painter.drawLine(
                        QPointF(x1 * prefs.edit.grid.x, y  * prefs.edit.grid.y),
                        QPointF(x2 * prefs.edit.grid.x, y  * prefs.edit.grid.y)
                    )
        # draw edge
        if prefs.draw.edge.enable:
            pen = QPen(prefs.display.edge.color, 0, Qt.PenStyle.SolidLine)
            brush = QBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(pen)
            painter.setBrush(brush)
            painter.drawRect(self.visibleRect)

    def resizeEvent(self : 'Canvas', event : QResizeEvent):
        if self.zoom is None:
            self.viewZoomAll()
        else:
            self._viewUpdate()
