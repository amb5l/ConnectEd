from PyQt6.QtCore import QPointF

from settings import settings


class CanvasApiViewMixin:
    def viewZoomAll(self : 'Canvas'):
        print(self.diagram.data)
        extents = self.diagram.extents()
        overscan = settings.prefs.display.overscan
        zoom_x = self.width()  / (extents.width()  + overscan.left + overscan.right)
        zoom_y = self.height() / (extents.height() + overscan.top  + overscan.bottom)
        self.zoom = min(zoom_x, zoom_y)
        self.pan = QPointF(-overscan.left, -overscan.top)
        self.zoomStatus()
        self._viewUpdate()

    def viewZoomSheet(self):
        pass

    def viewZoomSelection(self):
        pass

    def viewZoomIn(self,n=1):
        z1 = self.zoom
        z2 = min(self.zoom * (1.25**n), settings.prefs.display.zoom.max)
        dz = (1/z1) - (1/z2)
        self.pan.setX(self.pan.x() + (self.physicalPos.x() * dz))
        self.pan.setY(self.pan.y() + (self.physicalPos.y() * dz))
        self.zoom = z2
        self._actionEnable('View', 'zoomIn', self.zoom < settings.prefs.display.zoom.max)
        self.zoomStatus()
        self._viewUpdate()

    def viewZoomOut(self, n=1):
        z1 = self.zoom
        z2 = max(self.zoom / (1.25**n), settings.prefs.display.zoom.min)
        dz = (1/z1) - (1/z2)
        self.pan.setX(self.pan.x() + (self.physicalPos.x() * dz))
        self.pan.setY(self.pan.y() + (self.physicalPos.y() * dz))
        self.zoom = z2
        self._actionEnable('View', 'zoomOut', self.zoom > settings.prefs.display.zoom.min)
        self.zoomStatus()
        self._viewUpdate()

    def zoomStatus(self):
        self.main_window.statusbar.zoom.setText('{:.2f}'.format(self.zoom * 100))

    def viewPanLeft(self):
        self.pan.setX(self.pan.x() - settings.prefs.draw.panStep * self.width() / self.zoom)
        self._viewUpdate()

    def viewPanRight(self):
        self.pan.setX(self.pan.x() + settings.prefs.draw.panStep * self.width() / self.zoom)
        self._viewUpdate()

    def viewPanUp(self):
        self.pan.setY(self.pan.y() - settings.prefs.draw.panStep * self.height() / self.zoom)
        self._viewUpdate()

    def viewPanDown(self):
        self.pan.setY(self.pan.y() + settings.prefs.draw.panStep * self.height() / self.zoom)
        self._viewUpdate()

    def viewPrev(self):
        pass

    def viewNext(self):
        pass