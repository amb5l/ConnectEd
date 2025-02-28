from PyQt6.QtCore import QPointF, QRectF

from ...core import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Drawing


class DrawingPrivateMixin:
    def _p2l(self: 'Drawing', point: QPointF) -> QPointF:
        return (point / self.zoom) + self.pan

    def _l2p(self: 'Drawing', point: QPointF) -> QPointF:
        return (point - self.pan) * self.zoom

    def _viewUpdate(self: 'Drawing') -> None:
        #if self.mouse.current:
        #    self.main_window.statusbar.xy.setText(
        #        str(int(self.mouse.current.dpos.x())) + ',' +
        #        str(int(self.mouse.current.dpos.y()))
        #    )
        #else:
        #    self.main_window.statusbar.xy.setText('?,?')
        self.main_window.statusbar.zoom.setText('{:.2f}%'.format(self.zoom * 100))
        self.update()

    def _zoomUpdate(self: 'Drawing') -> None:
        #self.main_window.commands.actionEnable('viewZoomIn',  self.zoom < settings.prefs.view.zoom.max)
        #self.main_window.commands.actionEnable('viewZoomOut', self.zoom > settings.prefs.view.zoom.min)
        self._viewUpdate()

    def _zoomLRect(self: 'Drawing', lrect : QRectF) -> None:
        os = settings.prefs.display.overscan
        zoom_x = ( self.width()  - ( os.left + os.right  )) / lrect.width()
        zoom_y = ( self.height() - ( os.top  + os.bottom )) / lrect.height()
        self.zoom = min(zoom_x, zoom_y)
        self.pan = lrect.topLeft() - (QPointF(os.left, os.top) * self.zoom)
        self._zoomUpdate()
