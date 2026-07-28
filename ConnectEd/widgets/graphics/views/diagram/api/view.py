from __future__ import annotations

from typing import Self

from PyQt6.QtCore import QPointF

from ......app import settings

from ......core.check import checked

from ....scenes import withScene

from typing import TYPE_CHECKING
from ..host import asDiagramView
if TYPE_CHECKING:
    from ....scenes.diagram import DiagramScene


class DiagramViewApiViewMixin:
    @withScene
    @checked
    def viewZoomAll(self : Self, scene : DiagramScene) -> None:
        host = asDiagramView(self)
        host._zoomRect(scene.allRect())

    @withScene
    @checked
    def viewZoomSheet(self : Self, scene : DiagramScene) -> None:
        host = asDiagramView(self)
        host._zoomRect(scene._sheet_rect)

    @checked
    def viewZoomArea(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.stateViewZoomArea1)

    @checked
    def viewZoomIn(self : Self, n: int | float = 1) -> None:
        host = asDiagramView(self)
        host._zoomRelMouse((1 + settings().get("display/zoom/step"))**n)

    @checked
    def viewZoomOut(self : Self, n: int | float = 1) -> None:
        host = asDiagramView(self)
        host._zoomRelMouse((1 - settings().get("display/zoom/step"))**n)

    @checked
    def viewPan(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.stateViewPan1)

    @checked
    def viewPanLeft(self : Self, n: int | float = 1) -> None:
        host = asDiagramView(self)
        host._pan(QPointF(settings().get("display/pan/step") * n, 0))

    @checked
    def viewPanRight(self : Self, n: int | float = 1) -> None:
        host = asDiagramView(self)
        host._pan(QPointF(-settings().get("display/pan/step") * n, 0))

    @checked
    def viewPanUp(self : Self, n: int | float = 1) -> None:
        host = asDiagramView(self)
        host._pan(QPointF(0, settings().get("display/pan/step") * n))

    @checked
    def viewPanDown(self : Self, n: int | float = 1) -> None:
        host = asDiagramView(self)
        host._pan(QPointF(0, -settings().get("display/pan/step") * n))

    @checked
    def viewPrev(self : Self) -> None:
        raise NotImplementedError("viewPrev not implemented")

    @checked
    def viewNext(self : Self) -> None:
        raise NotImplementedError("viewNext not implemented")

    @checked
    def viewGridDisplay(self : Self, checked : bool) -> None:
        host = asDiagramView(self)
        host.grid.display = checked
        if (viewport := host.viewport()) is not None:
            viewport.update()

    @checked
    def viewGridSnap(self : Self, checked : bool) -> None:
        host = asDiagramView(self)
        host.grid.snap = checked

    @checked
    def viewGridPitch(self : Self, x : float, y : float) -> None:
        host = asDiagramView(self)
        host.grid.pitch = QPointF(x, y)
        if (viewport := host.viewport()) is not None:
            viewport.update()

    @checked
    def viewGridSettings(self : Self) -> None:
        raise NotImplementedError("viewGridSettings not implemented")
