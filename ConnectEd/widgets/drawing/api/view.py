from PyQt6.QtCore import QRect

from ....core import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from .. import Drawing


class DrawingApiViewMixin:
    def viewRefresh(self : 'Drawing'):
        self._viewUpdate()

    def viewZoomFull(self : 'Drawing'):
        # TODO get Drawing contents extents
        self._zoomDRect(QRect(self.origin.getOffset(), self.sheet))

    def viewZoomSheet(self : 'Drawing'):
        self._zoomDRect(QRect(self.origin.getOffset(), self.sheet))

    def viewZoomWindow(self : 'Drawing'):
        self.state = self.State.ViewZoomWindow1
        self._viewUpdate()

    # TODO add common function to do heavy lifting for zoom in/out

    def viewZoomIn(self : 'Drawing', n=1):
        self._zoomPanMouse(min(self.zoom * ((1+settings.prefs.view.zoom.step)**n), settings.prefs.view.zoom.max))

    def viewZoomOut(self : 'Drawing', n=1):
        self._zoomPanMouse(max(self.zoom * ((1+settings.prefs.view.zoom.step)**(-n)), settings.prefs.view.zoom.min))

    def viewPanLeft(self : 'Drawing'):
        self.pan.setX(self.pan.x() - (settings.prefs.view.pan_step * self.width() / self.zoom))
        self._viewUpdate()

    def viewPanRight(self : 'Drawing'):
        self.pan.setX(self.pan.x() + (settings.prefs.view.pan_step * self.width() / self.zoom))
        self._viewUpdate()

    def viewPanUp(self : 'Drawing'):
        self.pan.setY(self.pan.y() - (settings.prefs.view.pan_step * self.height() / self.zoom))
        self._viewUpdate()

    def viewPanDown(self : 'Drawing'):
        self.pan.setY(self.pan.y() + (settings.prefs.view.pan_step * self.height() / self.zoom))
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

