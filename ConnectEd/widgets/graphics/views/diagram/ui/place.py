from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DiagramViewUi


class DiagramViewUiPlaceMixin:
    def placePort(self : "DiagramViewUi") -> None:
        self._view.state.go(self._view.statePlacePort)

    def placeGate(self : "DiagramViewUi") -> None:
        self._view.state.go(self._view.statePlaceGate)

    def placeBlock(self : "DiagramViewUi") -> None:
        self._view.state.go(self._view.statePlaceBlock1)

    def placeBlockPin(self : "DiagramViewUi") -> None:
        self._view.state.go(self._view.statePlaceBlockPin)

    def placeSymbolPin(self : "DiagramViewUi") -> None:
        self._view.state.go(self._view.statePlaceSymbolPin)

    def placeConnection(self : "DiagramViewUi") -> None:
        self._view.state.go(self._view.statePlaceConn1)

    def placeTap(self : "DiagramViewUi") -> None:
        self._view.state.go(self._view.statePlaceTap)
