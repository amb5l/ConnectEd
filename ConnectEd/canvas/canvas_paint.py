from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QBrush

from prefs import prefs


class CanvasPaintMixin:
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.scale(self.zoom, self.zoom)
        painter.translate(-self.pan)
        painter.save()
        # draw background
        painter.fillRect(self.visibleRect, prefs().draw.theme.background)
        # draw sheet
        painter.fillRect(
            QRectF(
                self.canvas2diagram(QPointF(0, 0)),
                self.canvas2diagram(QPointF(
                    self.diagram.extents.width(),
                    self.diagram.extents.height()
                ))
            ),
            prefs().draw.theme.sheet
        )
        # draw border
        # draw title block
        # draw grid
        if prefs().edit.grid.enable:
            x1 = int( self.gridRect.left()   / prefs().edit.grid.x )
            y1 = int( self.gridRect.top()    / prefs().edit.grid.y )
            x2 = int( self.gridRect.right()  / prefs().edit.grid.x )
            y2 = int( self.gridRect.bottom() / prefs().edit.grid.y )
            pen = QPen(prefs().draw.theme.grid, 0, Qt.PenStyle.SolidLine)
            brush = QBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(pen)
            painter.setBrush(brush)
            for x in range(x1, x2+1):
                painter.drawLine(
                    QPointF(x  * prefs().edit.grid.x, y1 * prefs().edit.grid.y),
                    QPointF(x  * prefs().edit.grid.x, y2 * prefs().edit.grid.y)
                )
            for y in range(y1, y2+1):
                painter.drawLine(
                    QPointF(x1 * prefs().edit.grid.x, y  * prefs().edit.grid.y),
                    QPointF(x2 * prefs().edit.grid.x, y  * prefs().edit.grid.y)
                )
        # draw diagram - template, elements, decorations
        painter.restore()
        self.diagram.draw(painter, self.alpha)
        # edit state dependant drawing
        match self.editState:
            # draw selection box
            case self.EditState.SELECT_BOX:
                pen = QPen(prefs().draw.theme.selected.line, 0, Qt.PenStyle.DotLine)
                brush = QBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(pen)
                painter.setBrush(brush)
                painter.drawRect(QRectF(self.startPos, self.currentPos))
            # draw query hover text
            case self.EditState.QUERY:
                if self.queryItem is not None:
                    # TODO draw query text
                    pass
        # draw edge
        if prefs().draw.edge.enable:
            pen = QPen(prefs().draw.edge.color, 0, Qt.PenStyle.SolidLine)
            brush = QBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(pen)
            painter.setBrush(brush)
            painter.drawRect(self.visibleRect)

    def resizeEvent(self, event):
        if not self.initialResizeDone:
            self.zoomFull()
            self.initialResizeDone = True
        self._viewUpdate()

    # update visibleRect and gridRect after zoom or pan or window resize
    def _viewUpdate(self):
        self.visibleRect = QRectF(
            self.canvas2diagram(QPointF(0, 0)),
            self.canvas2diagram(QPointF(self.width()-1, self.height()-1))
        )
        self.gridRect = QRectF(
            self.visibleRect.topLeft()     - QPointF(prefs().edit.grid.x, prefs().edit.grid.y),
            self.visibleRect.bottomRight() + QPointF(prefs().edit.grid.x, prefs().edit.grid.y)
        )
        self.update()