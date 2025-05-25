from typing import Self

from PyQt6.QtCore import QPointF

from .defs import DrawingViewState as State


class DrawingViewViewMixin:

    def viewZoomAll(self : Self) -> None:
        rect = self._allItemsRect()
        if rect is None:
            self._zoomAbs(1)
        else:
            self._zoomRect(rect)

    def viewZoomWindow(self : Self) -> None:
        self._goState(State.ViewZoomWindow1)

    def viewZoomIn(self : Self, n : int = 1) -> None:
        from .....core import hub
        self._zoomRelMouse((1 + hub.settings.get("display/zoom/step"))**n)

    def viewZoomOut(self : Self, n : int = 1) -> None:
        from .....core import hub
        self._zoomRelMouse((1 - hub.settings.get("display/zoom/step"))**n)

    def viewPan(self : Self, n : int = 1) -> None:
        self._goState(State.ViewPan1)

    def viewPanLeft(self : Self, n : int = 1) -> None:
        from .....core import hub
        self._pan(QPointF(hub.settings.get("display/pan/step") * n, 0))

    def viewPanRight(self : Self, n : int = 1) -> None:
        from .....core import hub
        self._pan(QPointF(-hub.settings.get("display/pan/step") * n, 0))

    def viewPanUp(self : Self, n : int = 1) -> None:
        from .....core import hub
        self._pan(QPointF(0, hub.settings.get("display/pan/step") * n))

    def viewPanDown(self : Self, n : int = 1) -> None:
        from .....core import hub
        self._pan(QPointF(0, -hub.settings.get("display/pan/step") * n))

    def viewPrev(self : Self) -> None:
        pass

    def viewNext(self : Self) -> None:
        pass

    def viewGridDisplay(self : Self, checked : bool) -> None:
        self.grid.display = checked
        self.viewport().update()

    def viewGridSnap(self : Self, checked : bool) -> None:
        self.grid.snap = checked

    def viewGridSettings(self : Self) -> None:
        # TODO dialog required
        pass
