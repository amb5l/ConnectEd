from PyQt6.QtCore import QPointF

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingView


class DrawingViewViewMixin:

    def viewZoomAll(self : "DrawingView") -> None:
        rect = self._allItemsRect()
        if rect is None:
            self._zoomAbs(1)
        else:
            self._zoomRect(rect)

    def viewZoomArea(self : "DrawingView") -> None:
        self.state.go(self.stateViewZoomArea1)

    def viewZoomIn(self : "DrawingView", n : int = 1) -> None:
        from ..... import hub
        self._zoomRelMouse((1 + hub.settings.get("display/zoom/step"))**n)

    def viewZoomOut(self : "DrawingView", n : int = 1) -> None:
        from ..... import hub
        self._zoomRelMouse((1 - hub.settings.get("display/zoom/step"))**n)

    def viewPan(self : "DrawingView", n : int = 1) -> None:
        self.state.go(self.stateViewPan1)

    def viewPanLeft(self : "DrawingView", n : int = 1) -> None:
        from ..... import hub
        self._pan(QPointF(hub.settings.get("display/pan/step") * n, 0))

    def viewPanRight(self : "DrawingView", n : int = 1) -> None:
        from ..... import hub
        self._pan(QPointF(-hub.settings.get("display/pan/step") * n, 0))

    def viewPanUp(self : "DrawingView", n : int = 1) -> None:
        from ..... import hub
        self._pan(QPointF(0, hub.settings.get("display/pan/step") * n))

    def viewPanDown(self : "DrawingView", n : int = 1) -> None:
        from ..... import hub
        self._pan(QPointF(0, -hub.settings.get("display/pan/step") * n))

    def viewPrev(self : "DrawingView") -> None:
        pass

    def viewNext(self : "DrawingView") -> None:
        pass

    def viewGridDisplay(self : "DrawingView", checked : bool) -> None:
        self.grid.display = checked
        self.viewport().update()

    def viewGridSnap(self : "DrawingView", checked : bool) -> None:
        self.grid.snap = checked

    def viewGridSettings(self : "DrawingView") -> None:
        # TODO dialog required
        pass
