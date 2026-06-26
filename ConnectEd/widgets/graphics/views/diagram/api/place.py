from __future__ import annotations

from typing import Self, TypeAlias

from PyQt6.QtCore import QPointF

from ......core.check import checked

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....items.segment import SegmentItem
    from .. import DiagramView
    MixinSelf: TypeAlias = Self | DiagramView
else:
    MixinSelf = Self


class DiagramViewApiPlaceMixin:
    @checked
    def placePort(self : MixinSelf) -> None:
        self.state.go(self.statePlacePort)

    @checked
    def placeGate(self : MixinSelf) -> None:
        self.state.go(self.statePlaceGate)

    @checked
    def placeBlock(self : MixinSelf) -> None:
        self.state.go(self.statePlaceBlock1)

    @checked
    def placeBlockPin(self : MixinSelf) -> None:
        self.state.go(self.statePlaceBlockPin)

    @checked
    def placeSymbolPin(self : MixinSelf) -> None:
        self.state.go(self.statePlaceSymbolPin)

    @checked
    def placeConnection(self : MixinSelf) -> None:
        self.state.go(self.statePlaceConn1)

    @checked
    def placeTap(self : MixinSelf) -> None:
        self.state.go(self.statePlaceTap)

    @checked
    def placeNetLabel(self : MixinSelf) -> None:
        self.state.go(self.statePlaceNetLabel)

    @checked
    def placeNetLabelOnSegment(
        self     : MixinSelf,
        segment  : SegmentItem,
        spos     : QPointF | None = None
    ) -> None:
        if spos is None:
            spos = segment.sceneMidpoint()
        self.state.go(
            self.statePlaceNetLabelOnSegment,
            [segment],
            spos=spos
        )
