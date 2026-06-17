from __future__ import annotations

from typing import Self, TypeAlias

from PyQt6.QtCore import QPointF

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....items.segment import SegmentItem
    from .. import DiagramView
    MixinSelf: TypeAlias = Self | DiagramView
else:
    MixinSelf = Self


class DiagramViewApiPlaceMixin:
    def placePort(self : MixinSelf) -> None:
        self.state.go(self.statePlacePort)

    def placeGate(self : MixinSelf) -> None:
        self.state.go(self.statePlaceGate)

    def placeBlock(self : MixinSelf) -> None:
        self.state.go(self.statePlaceBlock1)

    def placeBlockPin(self : MixinSelf) -> None:
        self.state.go(self.statePlaceBlockPin)

    def placeSymbolPin(self : MixinSelf) -> None:
        self.state.go(self.statePlaceSymbolPin)

    def placeConnection(self : MixinSelf) -> None:
        self.state.go(self.statePlaceConn1)

    def placeTap(self : MixinSelf) -> None:
        self.state.go(self.statePlaceTap)

    def placeNetLabel(self : MixinSelf) -> None:
        self.state.go(self.statePlaceNetLabel)

    def placeNetLabelOnSegment(
        self     : MixinSelf,
        segment  : "SegmentItem",
        spos     : QPointF | None = None
    ) -> None:
        if spos is None:
            spos = segment.sceneMidpoint()
        self.state.go(
            self.statePlaceNetLabelOnSegment,
            [segment],
            spos=spos
        )
