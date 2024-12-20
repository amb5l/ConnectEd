from PyQt6.QtCore import QPointF, QRectF

from settings import settings


class CanvasPrivateMixin:

    def _canvas2diagram(self, point):
        # convert canvas point to diagram point
        r = QPointF(
            (point.x() / self.zoom) + self.pan.x(),
            (point.y() / self.zoom) + self.pan.y()
        )
        return r

    '''
    Update visibleRect and gridRect after zoom or pan or window resize
    '''
    def _viewUpdate(self):
        prefs = settings.prefs
        self.visibleRect = QRectF(
            self._canvas2diagram(QPointF(0, 0)),
            self._canvas2diagram(QPointF(self.width()-1, self.height()-1))
        )
        self.gridRect = QRectF(
            self.visibleRect.topLeft()     - QPointF(prefs.edit.grid.x, prefs.edit.grid.y),
            self.visibleRect.bottomRight() + QPointF(prefs.edit.grid.x, prefs.edit.grid.y)
        )
        self.update()
