from PyQt6.QtCore import QPoint, QRect, QSize

from ....core import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from .. import Drawing


class DrawingApiViewMixin:
    def viewRefresh(self : 'Drawing') -> None:
        self._viewUpdate()

    def viewZoomAll(self : 'Drawing') -> None:
        # TODO get Drawing contents extents
        self._zoomLRect(QRect(QPoint(0, 0), self.sheet))

    def viewZoomSheet(self : 'Drawing') -> None:
        self._zoomLRect(QRect(QPoint(0, 0), self.sheet))

    def viewZoomWindow(self : 'Drawing') -> None:
        self.state = self.State.ViewZoomWindow1

    def viewZoomIn(self : 'Drawing', n=1) -> None:
        self._zoomPanMouse(min(
            self.zoom * ((1+settings.prefs.display.zoom.step)**n),
            settings.prefs.display.zoom.limit.max
        ))

    def viewZoomOut(self : 'Drawing', n=1) -> None:
        self._zoomPanMouse(max(
            self.zoom * ((1+settings.prefs.display.zoom.step)**(-n)),
            settings.prefs.display.zoom.limit.min
        ))

    def viewPanLeft(self : 'Drawing') -> None:
        self.pan.setX(
            self.pan.x() - (settings.prefs.display.pan_step * self.width() / self.zoom))
        self._viewUpdate()

    def viewPanRight(self : 'Drawing') -> None:
        self.pan.setX(self.pan.x() + (settings.prefs.display.pan_step * self.width() / self.zoom))
        self._viewUpdate()

    def viewPanUp(self : 'Drawing') -> None:
        self.pan.setY(self.pan.y() - (settings.prefs.display.pan_step * self.height() / self.zoom))
        self._viewUpdate()

    def viewPanDown(self : 'Drawing') -> None:
        self.pan.setY(self.pan.y() + (settings.prefs.display.pan_step * self.height() / self.zoom))
        self._viewUpdate()

    def viewPrev(self : 'Drawing') -> None:
        pass

    def viewNext(self : 'Drawing') -> None:
        pass

    def viewGridSnap(self : 'Drawing') -> None:
        self.grid.snap = not self.grid.snap

    def viewGridDisplay(self : 'Drawing') -> None:
        self.grid.display = not self.grid.display
        self._viewUpdate()

    def viewGridSettings(self : 'Drawing') -> None:
        # TODO dialog required
        pass

