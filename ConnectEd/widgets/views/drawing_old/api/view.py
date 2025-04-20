from typing import Self

from PyQt6.QtCore import QPointF, QRectF, QSizeF

from ..... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from .. import DrawingView


class DrawingApiViewMixin:
    def viewZoomAll(self : Self) -> None:
        rect = self._allItemsRect()
        if rect is None:
            self._zoomAbs(1)
        else:
            self._zoomRect(rect)

    def viewZoomWindow(self : Self) -> None:
        self._goState(self.State.ViewZoomWindow1)

    def viewZoomIn(self : Self, n : int = 1) -> None:
        self._zoomRelMouse((1 + hub.settings.prefs.display.zoom.step)**n)

    def viewZoomOut(self : Self, n : int = 1) -> None:
        self._zoomRelMouse((1 - hub.settings.prefs.display.zoom.step)**n)

    def viewPan(self : Self, n : int = 1) -> None:
        self._goState(self.State.ViewPan1)

    def viewPanLeft(self : Self, n : int = 1) -> None:
        self._pan(QPointF(hub.settings.prefs.display.pan.step * n, 0))

    def viewPanRight(self : Self, n : int = 1) -> None:
        self._pan(QPointF(-hub.settings.prefs.display.pan.step * n, 0))

    def viewPanUp(self : Self, n : int = 1) -> None:
        self._pan(QPointF(0, hub.settings.prefs.display.pan.step * n))

    def viewPanDown(self : Self, n : int = 1) -> None:
        self._pan(QPointF(0, -hub.settings.prefs.display.pan.step * n))

    def viewPrev(self : Self) -> None:
        pass

    def viewNext(self : Self) -> None:
        pass

    def viewGridDisplay(self : Self, checked : bool) -> None:
        self.grid.setVisible(checked)

    def viewGridSnap(self : Self, checked : bool) -> None:
        self.grid.snap = checked

    def viewGridSettings(self : Self) -> None:
        # TODO dialog required
        pass
