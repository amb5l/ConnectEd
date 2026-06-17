from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DiagramViewUi
    from ....items.segment import SegmentItem

from PyQt6.QtCore import QPointF


class DiagramViewApiPlaceMixin:
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

    def placeNetLabel(self : "DiagramViewUi") -> None:
        self._view.state.go(self._view.statePlaceNetLabel)

    def placeNetLabelOnSegment(
        self     : "DiagramViewUi",
        segment  : "SegmentItem",
        spos     : QPointF | None = None
    ) -> None:
        if spos is None:
            spos = segment.sceneMidpoint()
        self._view.state.go(
            self._view.statePlaceNetLabelOnSegment,
            [segment],
            spos=spos
        )