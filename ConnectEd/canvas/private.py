class CanvasPrivateMixin:
    '''
    Update visibleRect and gridRect after zoom or pan or window resize
    '''
    def _viewUpdate(self):
        self.visibleRect = QRectF(
            self.canvas2diagram(QPointF(0, 0)),
            self.canvas2diagram(QPointF(self.width()-1, self.height()-1))
        )
        self.gridRect = QRectF(
            self.visibleRect.topLeft()     - QPointF(prefs.edit.grid.x, prefs.edit.grid.y),
            self.visibleRect.bottomRight() + QPointF(prefs.edit.grid.x, prefs.edit.grid.y)
        )
        self.update()
