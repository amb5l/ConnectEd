from PyQt6.QtCore import QPointF

from settings import prefs


class CanvasApiViewMixin:
    def viewZoomAll(self):
        extents_x = max(self.diagram.extents.width(), self.diagram.sheet.width())
        extents_y = max(self.diagram.extents.height(), self.diagram.sheet.height())
        m = prefs.display.margin
        zoom_x = self.width()  / (extents_x + m.left + m.right)
        zoom_y = self.height() / (extents_y + m.top  + m.bottom)
        self.zoom = min(zoom_x, zoom_y)
        self.pan = QPointF(-m.left, -m.top)
        self._actionEnable('View', 'zoomIn',  self.zoom < prefs.display.zoom.max)
        self._actionEnable('View', 'zoomOut', self.zoom > prefs.display.zoom.min)
        self.zoomStatus()
        self._viewUpdate()

    def viewZoomSheet(self):
        pass

    def viewZoomSelection(self):
        pass

    def viewZoomIn(self,n=1):
        z1 = self.zoom
        z2 = min(self.zoom * (1.25**n), prefs.display.zoom.max)
        dz = (1/z1) - (1/z2)
        self.pan.setX(self.pan.x() + (self.physicalPos.x() * dz))
        self.pan.setY(self.pan.y() + (self.physicalPos.y() * dz))
        self.zoom = z2
        self._actionEnable('View', 'zoomIn', self.zoom < prefs.display.zoom.max)
        self.zoomStatus()
        self._viewUpdate()

    def viewZoomOut(self, n=1):
        z1 = self.zoom
        z2 = max(self.zoom / (1.25**n), prefs.display.zoom.min)
        dz = (1/z1) - (1/z2)
        self.pan.setX(self.pan.x() + (self.physicalPos.x() * dz))
        self.pan.setY(self.pan.y() + (self.physicalPos.y() * dz))
        self.zoom = z2
        self._actionEnable('View', 'zoomOut', self.zoom > prefs.display.zoom.min)
        self.zoomStatus()
        self._viewUpdate()

    def zoomStatus(self):
        z = int(self.zoom * 100)
        self.window().statusBar.zoom.setText(f'Scale = {z}%')

    def viewPanLeft(self):
        self.pan.setX(self.pan.x() - prefs.draw.panStep * self.width() / self.zoom)
        self._viewUpdate()

    def viewPanRight(self):
        self.pan.setX(self.pan.x() + prefs.draw.panStep * self.width() / self.zoom)
        self._viewUpdate()

    def viewPanUp(self):
        self.pan.setY(self.pan.y() - prefs.draw.panStep * self.height() / self.zoom)
        self._viewUpdate()

    def viewPanDown(self):
        self.pan.setY(self.pan.y() + prefs.draw.panStep * self.height() / self.zoom)
        self._viewUpdate()

    def viewPrev(self):
        pass

    def viewNext(self):
        pass