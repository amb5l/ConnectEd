from PyQt6.QtCore import QPointF

from settings import prefs


class CanvasZoomPanMixin:
    def zoomFull(self):
        self.zoom = min(
            self.width()  / ( self.diagram.extents.width()  + prefs.display.canvas.margin.left + prefs.display.canvas.margin.right  ),
            self.height() / ( self.diagram.extents.height() + prefs.display.canvas.margin.top  + prefs.display.canvas.margin.bottom )
        )
        self.pan = QPointF(-prefs.display.canvas.margin.left, -prefs.display.canvas.margin.top)
        self._actionEnable('View', 'zoomIn',  self.zoom < prefs.display.zoom.max)
        self._actionEnable('View', 'zoomOut', self.zoom > prefs.display.zoom.min)
        self.zoomStatus()
        self._viewUpdate()

    def zoomIn(self,n=1):
        z1 = self.zoom
        z2 = min(self.zoom * (1.25**n), prefs.display.zoom.max)
        dz = (1/z1) - (1/z2)
        self.pan.setX(self.pan.x() + (self.physicalPos.x() * dz))
        self.pan.setY(self.pan.y() + (self.physicalPos.y() * dz))
        self.zoom = z2
        self._actionEnable('View', 'zoomIn', self.zoom < prefs.display.zoom.max)
        self.zoomStatus()
        self._viewUpdate()

    def zoomOut(self, n=1):
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

    def panLeft(self):
        self.pan.setX(self.pan.x() - prefs.draw.panStep * self.width() / self.zoom)
        self._viewUpdate()

    def panRight(self):
        self.pan.setX(self.pan.x() + prefs.draw.panStep * self.width() / self.zoom)
        self._viewUpdate()

    def panUp(self):
        self.pan.setY(self.pan.y() - prefs.draw.panStep * self.height() / self.zoom)
        self._viewUpdate()

    def panDown(self):
        self.pan.setY(self.pan.y() + prefs.draw.panStep * self.height() / self.zoom)
        self._viewUpdate()
