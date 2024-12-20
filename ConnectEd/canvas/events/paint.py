from PyQt6.QtCore import Qt, QPointF, QRect
from PyQt6.QtGui  import QPaintEvent, QResizeEvent, QPainter, QPen, QBrush
from typing import TYPE_CHECKING

from settings import settings

if TYPE_CHECKING:
    from canvas import Canvas

class CanvasEventsPaintMixin:
    def paintEvent(self : 'Canvas', event : QPaintEvent):
        prefs = settings.prefs
        theme = settings.theme
        painter = QPainter(self)
        # draw void

        # get extents of visible portion of canvas
        self.visibleRect = QRect(0, 0, self.width()-1, self.height()-1)

        # draw background
        painter.fillRect(self.visibleRect, theme.background)
        # draw diagram
        if self.diagram.data is None:
            pass
        else:
            painter.scale(self.zoom, self.zoom)
            painter.translate(-self.pan)
            self.diagram.paint(painter)
        ## edit state dependant drawing
        #if self.State == self.State.SELECT_WIN_1:
        #    pen = QPen(prefs.draw.theme.selected.line, 0, Qt.PenStyle.DotLine)
        #    brush = QBrush(Qt.BrushStyle.NoBrush)
        #    painter.setPen(pen)
        #    painter.setBrush(brush)
        #    painter.drawRect(QRectF(self.startPos, self.currentPos))
        # draw grid
        if prefs.display.grid.enable:
            x1 = int( self.gridRect.left()   / prefs.edit.grid.x )
            y1 = int( self.gridRect.top()    / prefs.edit.grid.y )
            x2 = int( self.gridRect.right()  / prefs.edit.grid.x )
            y2 = int( self.gridRect.bottom() / prefs.edit.grid.y )
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
        # developer: canvas geometry
        if prefs.display.developer.canvas.geometry:
            pen = QPen(theme.edge, 0, Qt.PenStyle.SolidLine)
            brush = QBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(pen)
            painter.setBrush(brush)
            #painter.drawRect(self.visibleRect)
            painter.drawRect(QRect(self.visibleRect.topLeft(), self.visibleRect.bottomRight()))
            painter.drawLine(self.visibleRect.topLeft(), self.visibleRect.bottomRight())
            painter.drawLine(self.visibleRect.topRight(), self.visibleRect.bottomLeft())

    def resizeEvent(self : 'Canvas', event : QResizeEvent):
        if self.zoom is None:
            self.viewZoomAll()
        else:
            self._viewUpdate()
