from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...drawing import DrawingView
    from ...diagram import DiagramView
    from ...symbol  import SymbolView


class DrawingViewUiPlaceMixin:
    def placePort(self : "DiagramView") -> None:
        self.state.go(self.statePlacePort)

    def placeBlock(self : "DiagramView") -> None:
        self.state.go(self.statePlaceBlock1)

    def placeBlockPin(self : "DiagramView") -> None:
        self.state.go(self.statePlaceBlockPin)

    def placeSymbolPin(self : "SymbolView") -> None:
        self.state.go(self.statePlaceSymbolPin)

    def placeConnection(self : "DiagramView") -> None:
        self.state.go(self.statePlaceConn1)

    def placeLine(self : "DrawingView") -> None:
        self.state.go(self.statePlaceLine1)

    def placeRectangle(self : "DrawingView") -> None:
        self.state.go(self.statePlaceRectangle1)

    def placeText(self : "DrawingView") -> None:
        self.state.go(self.statePlaceText)

    def placeTextBlock(self : "DrawingView") -> None:
        self.state.go(self.statePlaceTextBlock)
