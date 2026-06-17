from typing import Self

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView
    MixinSelf = Self | DrawingView


class DrawingViewApiPlaceMixin:
    def placeLine(self : "MixinSelf") -> None:
        self.state.go(self.statePlaceLine1)

    def placeRectangle(self : "MixinSelf") -> None:
        self.state.go(self.statePlaceRectangle1)

    def placeEllipse(self : "MixinSelf") -> None:
        self.state.go(self.statePlaceEllipse1)

    def placePolyline(self : "MixinSelf") -> None:
        self.state.go(self.statePlacePolyline1)

    def placeText(self : "MixinSelf") -> None:
        self.state.go(self.statePlaceText)
