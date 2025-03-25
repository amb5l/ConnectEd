from PyQt6.QtCore import QPointF, QRectF, QSizeF

from ..... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from .. import DrawingView


class DrawingApiViewMixin:
    def viewZoomExtents(self : 'DrawingView') -> None:
        self._zoomRect(self.extents.rect())

    def viewZoomAll(self : 'DrawingView') -> None:
        self._zoomRect(self._allItemsRect())

    def viewZoomWindow(self : 'DrawingView') -> None:
        self._goState(self.State.ViewZoomWindow1)

    def viewZoomIn(self : 'DrawingView', n=1) -> None:
        self._zoomRelMouse((1 + hub.settings.prefs.display.zoom.step)**n)

    def viewZoomOut(self : 'DrawingView', n=1) -> None:
        self._zoomRelMouse((1 - hub.settings.prefs.display.zoom.step)**n)

    def viewPan(self : 'DrawingView', n=1) -> None:
        self._goState(self.State.ViewPan1)

    def viewPanLeft(self : 'DrawingView', n=1) -> None:
        self._pan(QPointF(hub.settings.prefs.display.pan.step * n, 0))

    def viewPanRight(self : 'DrawingView', n=1) -> None:
        self._pan(QPointF(-hub.settings.prefs.display.pan.step * n, 0))

    def viewPanUp(self : 'DrawingView', n=1) -> None:
        self._pan(QPointF(0, hub.settings.prefs.display.pan.step * n))

    def viewPanDown(self : 'DrawingView', n=1) -> None:
        self._pan(QPointF(0, -settings.prefs.display.pan.step * n))

    def viewPrev(self : 'DrawingView') -> None:
        pass

    def viewNext(self : 'DrawingView') -> None:
        pass

    def viewGridDisplay(self : 'DrawingView', checked : bool) -> None:
        self.grid.setVisible(checked)

    def viewGridSnap(self : 'DrawingView', checked : bool) -> None:
        self.grid.snap = checked

    def viewGridSettings(self : 'DrawingView') -> None:
        # TODO dialog required
        pass

