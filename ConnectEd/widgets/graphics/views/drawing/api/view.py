from __future__ import annotations

from typing import Self, TypeAlias

from PyQt6.QtCore import QPointF, QRectF

from ......app import settings

from ......core.check import checked

from ....scenes import withScene

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.drawing import DrawingScene
    from .. import DrawingView
    MixinSelf: TypeAlias = Self | DrawingView
else:
    MixinSelf = Self


class DrawingViewApiViewMixin:
    @withScene
    @checked
    def viewZoomAll(self : MixinSelf, scene : DrawingScene) -> None:
        scene.updateSceneRect()
        if scene.items():
            rect = self._allItemsRect()
        elif hasattr(scene, 'sheet'):
            rect = scene.sheet.rect
        else:
            rect = QRectF(QPointF(0, 0), settings().get("defaults/extents"))
        self._zoomRect(rect)

    @withScene
    @checked
    def viewZoomSheet(self : MixinSelf, scene : DrawingScene) -> None:
        rect = scene.sheet.rect
        self._zoomRect(rect)

    @checked
    def viewZoomArea(self : MixinSelf) -> None:
        self.state.go(self.stateViewZoomArea1)

    @checked
    def viewZoomIn(self : MixinSelf, n : int = 1) -> None:
        self._zoomRelMouse((1 + settings().get("display/zoom/step"))**n)

    @checked
    def viewZoomOut(self : MixinSelf, n : int = 1) -> None:
        self._zoomRelMouse((1 - settings().get("display/zoom/step"))**n)

    @checked
    def viewPan(self : MixinSelf) -> None:
        self.state.go(self.stateViewPan1)

    @checked
    def viewPanLeft(self : MixinSelf, n : int = 1) -> None:
        self._pan(QPointF(settings().get("display/pan/step") * n, 0))

    @checked
    def viewPanRight(self : MixinSelf, n : int = 1) -> None:
        self._pan(QPointF(-settings().get("display/pan/step") * n, 0))

    @checked
    def viewPanUp(self : MixinSelf, n : int = 1) -> None:
        self._pan(QPointF(0, settings().get("display/pan/step") * n))

    @checked
    def viewPanDown(self : MixinSelf, n : int = 1) -> None:
        self._pan(QPointF(0, -settings().get("display/pan/step") * n))

    @checked
    def viewPrev(self : MixinSelf) -> None:
        pass

    @checked
    def viewNext(self : MixinSelf) -> None:
        pass

    @checked
    def viewGridDisplay(self : MixinSelf, checked : bool) -> None:
        self.grid.display = checked
        self.viewport().update()

    @checked
    def viewGridSnap(self : MixinSelf, checked : bool) -> None:
        self.grid.snap = checked

    @checked
    def viewGridPitch(self : MixinSelf, x : float, y : float) -> None:
        self.grid.pitch = QPointF(x, y)
        self.viewport().update()

    @checked
    def viewGridSettings(self : MixinSelf) -> None:
        # TODO dialog required
        pass
