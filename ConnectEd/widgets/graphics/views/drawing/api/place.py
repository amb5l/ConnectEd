from __future__ import annotations

from typing import Self, TypeAlias

from ......core.check import checked

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView
    MixinSelf: TypeAlias = Self | DrawingView
else:
    MixinSelf = Self


class DrawingViewApiPlaceMixin:
    @checked
    def placeLine(self : MixinSelf) -> None:
        self.state.go(self.statePlaceLine1)

    @checked
    def placeRectangle(self : MixinSelf) -> None:
        self.state.go(self.statePlaceRectangle1)

    @checked
    def placeEllipse(self : MixinSelf) -> None:
        self.state.go(self.statePlaceEllipse1)

    @checked
    def placePolyline(self : MixinSelf) -> None:
        self.state.go(self.statePlacePolyline1)

    @checked
    def placeText(self : MixinSelf) -> None:
        self.state.go(self.statePlaceText)
