from PyQt6.QtCore    import QPointF, QRectF

from ......app import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.drawing import DrawingScene
    from .. import DrawingView


class DrawingViewUiViewMixin:

    def viewZoomAll(self : "DrawingView") -> None:
        scene : DrawingScene = self.scene()
        scene.updateSceneRect()
        if scene.items():
            rect = self._allItemsRect()
        elif hasattr(scene, 'sheet'):
            rect = scene.sheet.rect
        else:
            rect = QRectF(QPointF(0, 0), settings().get("defaults/extents"))
        self._zoomRect(rect)

    def viewZoomArea(self : "DrawingView") -> None:
        self.state.go(self.stateViewZoomArea1)

    def viewZoomIn(self : "DrawingView", n : int = 1) -> None:
        self._zoomRelMouse((1 + settings().get("display/zoom/step"))**n)

    def viewZoomOut(self : "DrawingView", n : int = 1) -> None:
        self._zoomRelMouse((1 - settings().get("display/zoom/step"))**n)

    def viewPan(self : "DrawingView", n : int = 1) -> None:
        self.state.go(self.stateViewPan1)

    def viewPanLeft(self : "DrawingView", n : int = 1) -> None:
        self._pan(QPointF(settings().get("display/pan/step") * n, 0))

    def viewPanRight(self : "DrawingView", n : int = 1) -> None:
        self._pan(QPointF(-settings().get("display/pan/step") * n, 0))

    def viewPanUp(self : "DrawingView", n : int = 1) -> None:
        self._pan(QPointF(0, settings().get("display/pan/step") * n))

    def viewPanDown(self : "DrawingView", n : int = 1) -> None:
        self._pan(QPointF(0, -settings().get("display/pan/step") * n))

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
