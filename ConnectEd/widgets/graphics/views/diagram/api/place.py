from __future__ import annotations

from typing import Self

from PyQt6.QtCore import QPointF

from ......core.check import checked

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....items.segment import SegmentItem


class DiagramViewApiPlaceMixin:
    @checked
    def placeLine(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.state.go(self.statePlaceLine1)

    @checked
    def placeRectangle(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.state.go(self.statePlaceRectangle1)

    @checked
    def placeEllipse(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.state.go(self.statePlaceEllipse1)

    @checked
    def placePolyline(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.state.go(self.statePlacePolyline1)

    @checked
    def placeText(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.state.go(self.statePlaceText)

    @checked
    def placePort(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.state.go(self.statePlacePort)

    @checked
    def placeGate(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.state.go(self.statePlaceGate)

    @checked
    def placeBlock(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.state.go(self.statePlaceBlock1)

    @checked
    def placeBlockPin(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.state.go(self.statePlaceBlockPin)

    @checked
    def placeSymbolPin(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.state.go(self.statePlaceSymbolPin)

    @checked
    def placeConnection(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.state.go(self.statePlaceConn1)

    @checked
    def placeTap(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.state.go(self.statePlaceTap)

    @checked
    def placeNetLabel(self : Self) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self.state.go(self.statePlaceNetLabel)

    @checked
    def placeNetLabelOnSegment(
        self     : Self,
        segment  : SegmentItem,
        spos     : QPointF | None = None
    ) -> None:
        from .. import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        if spos is None:
            spos = segment.sceneMidpoint()
        self.state.go(
            self.statePlaceNetLabelOnSegment,
            [segment],
            spos=spos
        )
