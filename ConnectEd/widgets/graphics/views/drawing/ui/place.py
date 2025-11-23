from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingViewUi


class DrawingViewUiPlaceMixin:
    def placePort(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.statePlacePort)

    def placeGate(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.statePlaceGate)

    def placeBlock(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.statePlaceBlock1)

    def placeBlockPin(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.statePlaceBlockPin)

    def placeSymbolPin(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.statePlaceSymbolPin)

    def placeConnection(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.statePlaceConn1)

    def placeLine(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.statePlaceLine1)

    def placeRectangle(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.statePlaceRectangle1)

    def placeEllipse(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.statePlaceEllipse1)

    def placePolyline(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.statePlacePolyline1)

    def placeTextLine(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.statePlaceTextLine)

    def placeTextBlock(self : "DrawingViewUi") -> None:
        self._view.state.go(self._view.statePlaceTextBlock)
