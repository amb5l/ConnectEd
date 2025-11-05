from PyQt6.QtCore import QPointF, QRectF

from ......app import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingViewUi


class DrawingViewUiViewMixin:
    def viewZoomAll(self : "DrawingViewUi") -> None:
        self._scene.updateSceneRect()
        if self._scene.items():
            rect = self._view._allItemsRect()
        elif hasattr(self._scene, 'sheet'):
            rect = self._scene.sheet.rect
        else:
            rect = QRectF(QPointF(0, 0), settings().get("defaults/extents"))
        self._view._zoomRect(rect)

    def viewZoomSheet(self : "DrawingViewUi") -> None:
        rect = self._scene.sheet.rect
        self._view._zoomRect(rect)

    def viewZoomArea(self : "DrawingViewUi") -> None:
        self.state.go(self.stateViewZoomArea1)

    def viewZoomIn(self : "DrawingViewUi", n : int = 1) -> None:
        self._view._zoomRelMouse((1 + settings().get("display/zoom/step"))**n)

    def viewZoomOut(self : "DrawingViewUi", n : int = 1) -> None:
        self._view._zoomRelMouse((1 - settings().get("display/zoom/step"))**n)

    def viewPan(self : "DrawingViewUi", n : int = 1) -> None:
        self.state.go(self.stateViewPan1)

    def viewPanLeft(self : "DrawingViewUi", n : int = 1) -> None:
        self._view._pan(QPointF(settings().get("display/pan/step") * n, 0))

    def viewPanRight(self : "DrawingViewUi", n : int = 1) -> None:
        self._view._pan(QPointF(-settings().get("display/pan/step") * n, 0))

    def viewPanUp(self : "DrawingViewUi", n : int = 1) -> None:
        self._view._pan(QPointF(0, settings().get("display/pan/step") * n))

    def viewPanDown(self : "DrawingViewUi", n : int = 1) -> None:
        self._view._pan(QPointF(0, -settings().get("display/pan/step") * n))

    def viewPrev(self : "DrawingViewUi") -> None:
        pass

    def viewNext(self : "DrawingViewUi") -> None:
        pass

    def viewGridDisplay(self : "DrawingViewUi", checked : bool) -> None:
        self._view.grid.display = checked
        self._view.viewport().update()

    def viewGridSnap(self : "DrawingViewUi", checked : bool) -> None:
        self._view.grid.snap = checked

    def viewGridPitch(self : "DrawingViewUi", pitch_x : float, pitch_y : float) -> None:
        self._view.grid.pitch = QPointF(pitch_x, pitch_y)
        self._view.viewport().update()

    def viewGridSettings(self : "DrawingViewUi") -> None:
        # TODO dialog required
        pass
