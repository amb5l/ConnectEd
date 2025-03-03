from PyQt6.QtCore import QPoint, QRect, QSize

from ....core import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from .. import Drawing


class DrawingApiViewMixin:
    def viewRefresh(self : 'Drawing'):
        self._viewUpdate()

    def viewZoomAll(self : 'Drawing'):
        # TODO get Drawing contents extents
        self._zoomLRect(QRect(QPoint(0, 0), self.sheet))

    def viewZoomSheet(self : 'Drawing'):
        self._zoomLRect(QRect(QPoint(0, 0), self.sheet))

    def viewZoomWindow(self : 'Drawing'):
        self.state = self.State.ViewZoomWindow1
        self._viewUpdate()

    def viewZoomIn(self : 'Drawing', n=1):
        self._zoomPanMouse(min(self.zoom * ((1+settings.prefs.display.zoom.step)**n), settings.prefs.display.zoom.max))

    def viewZoomOut(self : 'Drawing', n=1):
        self._zoomPanMouse(max(self.zoom * ((1+settings.prefs.display.zoom.step)**(-n)), settings.prefs.display.zoom.min))

    def viewPanLeft(self : 'Drawing'):
        self.pan.setX(self.pan.x() - (settings.prefs.display.pan_step * self.width() / self.zoom))
        self._viewUpdate()

    def viewPanRight(self : 'Drawing'):
        self.pan.setX(self.pan.x() + (settings.prefs.display.pan_step * self.width() / self.zoom))
        self._viewUpdate()

    def viewPanUp(self : 'Drawing'):
        self.pan.setY(self.pan.y() - (settings.prefs.display.pan_step * self.height() / self.zoom))
        self._viewUpdate()

    def viewPanDown(self : 'Drawing'):
        self.pan.setY(self.pan.y() + (settings.prefs.display.pan_step * self.height() / self.zoom))
        self._viewUpdate()

    def viewPrev(self : 'Drawing'):
        pass

    def viewNext(self : 'Drawing'):
        pass

    def viewGridSnap(self : 'Drawing'):
        self.grid.snap = not self.grid.snap

    def viewGridDisplay(self : 'Drawing'):
        self.grid.display = not self.grid.display
        self._viewUpdate()

    def viewGridSettings(self : 'Drawing'):
        # TODO dialog required
        pass

