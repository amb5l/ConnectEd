from __future__ import annotations

from typing import Self

from PyQt6.QtCore import QPointF

from ......app import settings

from ......core.check import checked

from ....scenes import withScene

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.diagram import DiagramScene


class DiagramViewApiViewMixin:
    @withScene
    @checked
    def viewZoomAll(self : Self, scene : DiagramScene) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self._zoomRect(scene.allRect())

    @withScene
    @checked
    def viewZoomSheet(self : Self, scene : DiagramScene) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self._zoomRect(scene._sheet_rect)

    @checked
    def viewZoomArea(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.state.go(self.stateViewZoomArea1)

    @checked
    def viewZoomIn(self : Self, n: int | float = 1) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self._zoomRelMouse((1 + settings().get("display/zoom/step"))**n)

    @checked
    def viewZoomOut(self : Self, n: int | float = 1) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self._zoomRelMouse((1 - settings().get("display/zoom/step"))**n)

    @checked
    def viewPan(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.state.go(self.stateViewPan1)

    @checked
    def viewPanLeft(self : Self, n: int | float = 1) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self._pan(QPointF(settings().get("display/pan/step") * n, 0))

    @checked
    def viewPanRight(self : Self, n: int | float = 1) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self._pan(QPointF(-settings().get("display/pan/step") * n, 0))

    @checked
    def viewPanUp(self : Self, n: int | float = 1) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self._pan(QPointF(0, settings().get("display/pan/step") * n))

    @checked
    def viewPanDown(self : Self, n: int | float = 1) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self._pan(QPointF(0, -settings().get("display/pan/step") * n))

    @checked
    def viewPrev(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        raise NotImplementedError("viewPrev not implemented")

    @checked
    def viewNext(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        raise NotImplementedError("viewNext not implemented")

    @checked
    def viewGridDisplay(self : Self, checked : bool) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.grid.display = checked
        if (viewport := self.viewport()) is not None:
            viewport.update()

    @checked
    def viewGridSnap(self : Self, checked : bool) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.grid.snap = checked

    @checked
    def viewGridPitch(self : Self, x : float, y : float) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.grid.pitch = QPointF(x, y)
        if (viewport := self.viewport()) is not None:
            viewport.update()

    @checked
    def viewGridSettings(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        raise NotImplementedError("viewGridSettings not implemented")
