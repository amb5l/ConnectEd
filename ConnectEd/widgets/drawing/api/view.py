from PyQt6.QtCore import QPointF, QRectF, QSizeF

from ....core import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from .. import Drawing


class DrawingApiViewMixin:
    def viewRefresh(self : 'Drawing') -> None:
        self._zoomUpdate()

    def viewZoomAll(self : 'Drawing') -> None:
        # TODO get Drawing contents extents
        self._zoomLRect(QRectF(QPointF(0, 0), QSizeF(self.sheet)))

    def viewZoomSheet(self : 'Drawing') -> None:
        self._zoomLRect(QRectF(QPointF(0, 0), QSizeF(self.sheet)))

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

    def viewCenter(self : 'Drawing') -> None:
        self.state = self.State.ViewCenter

    def viewPan(self : 'Drawing') -> None:
        self.state = self.State.ViewPan1

    def viewPanLeft(self : 'Drawing') -> None:
        self.pan.setX(
            self.pan.x() - (settings.prefs.display.pan.step * self.width() / self.zoom))
        self._panUpdate()

    def viewPanRight(self : 'Drawing') -> None:
        self.pan.setX(self.pan.x() + (settings.prefs.display.pan.step * self.width() / self.zoom))
        self._panUpdate()

    def viewPanUp(self : 'Drawing') -> None:
        self.pan.setY(self.pan.y() - (settings.prefs.display.pan.step * self.height() / self.zoom))
        self._panUpdate()

    def viewPanDown(self : 'Drawing') -> None:
        self.pan.setY(self.pan.y() + (settings.prefs.display.pan.step * self.height() / self.zoom))
        self._panUpdate()

    def viewPrev(self : 'Drawing') -> None:
        pass

    def viewNext(self : 'Drawing') -> None:
        pass

    def viewGridDisplay(self : 'Drawing', checked : bool) -> None:
        self.grid.display = checked
        self.update()

    def viewGridSnap(self : 'Drawing', checked : bool) -> None:
        self.grid.snap = checked

    def viewGridSettings(self : 'Drawing') -> None:
        # TODO dialog required
        pass

