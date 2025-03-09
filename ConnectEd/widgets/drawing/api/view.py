from PyQt6.QtCore import QPointF, QRectF, QSizeF

from ....core import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from .. import Drawing


class DrawingApiViewMixin:
    def viewZoomAll(self : 'Drawing') -> None:
        """
        Zoom to show all content in the scene, focusing precisely on the items.
        The scene rectangle is still set to include minimum extents for proper scrolling limits.
        """
        # Get the bounding rectangle of all scene items
        items_rect = self._boundingRect()

        # Set scene rectangle to include minimum extents (for proper scrolling limits)
        # but zoom specifically to just the items
        self.setSceneRect(items_rect.united(self._minExtents()))

        # Zoom to show exactly the items (not the extended scene rectangle)
        self._zoomRect(items_rect)

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
        self.grid.display = checked
        self.update()

    def viewGridSnap(self : 'Drawing', checked : bool) -> None:
        self.grid.snap = checked

    def viewGridSettings(self : 'Drawing') -> None:
        # TODO dialog required
        pass

