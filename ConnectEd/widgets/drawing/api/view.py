from PyQt6.QtCore import QPointF, QRectF, QSizeF

from ....core import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from .. import Drawing


class DrawingApiViewMixin:
    def viewZoomExtents(self : 'Drawing') -> None:
        self._zoomRect(self.extents.rect())

    def viewZoomAll(self : 'Drawing') -> None:
        self._zoomRect(self._itemsRect())

    def viewZoomWindow(self : 'Drawing') -> None:
        self.state = self.State.ViewZoomWindow1

    def viewZoomIn(self : 'Drawing', n=1) -> None:
        self._zoomRelMouse((1 + settings.prefs.display.zoom.step)**n)

    def viewZoomOut(self : 'Drawing', n=1) -> None:
        self._zoomRelMouse((1 - settings.prefs.display.zoom.step)**n)

    def viewCenter(self : 'Drawing') -> None:
        self.state = self.State.ViewCenter

    def viewPanLeft(self : 'Drawing', n=1) -> None:
        self._pan(QPointF(settings.prefs.display.pan.step * n, 0))

    def viewPanRight(self : 'Drawing', n=1) -> None:
        self._pan(QPointF(-settings.prefs.display.pan.step * n, 0))

    def viewPanUp(self : 'Drawing', n=1) -> None:
        self._pan(QPointF(0, settings.prefs.display.pan.step * n))

    def viewPanDown(self : 'Drawing', n=1) -> None:
        self._pan(QPointF(0, -settings.prefs.display.pan.step * n))

    def viewPrev(self : 'Drawing') -> None:
        pass

    def viewNext(self : 'Drawing') -> None:
        pass

    def viewGridDisplay(self : 'Drawing', checked : bool) -> None:
        self.grid.setVisible(checked)

    def viewGridSnap(self : 'Drawing', checked : bool) -> None:
        self.grid.snap = checked

    def viewGridSettings(self : 'Drawing') -> None:
        # TODO dialog required
        pass

