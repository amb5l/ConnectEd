from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingViewUi


class DrawingViewUiPlaceMixin:
    def placeLine(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.statePlaceLine1)

    def placeRectangle(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.statePlaceRectangle1)

    def placeEllipse(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.statePlaceEllipse1)

    def placePolyline(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.statePlacePolyline1)

    def placeText(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.statePlaceText)
