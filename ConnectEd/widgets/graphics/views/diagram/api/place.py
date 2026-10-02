from __future__ import annotations

from typing import Self

from PyQt6.QtCore import QPointF

from ......app import logger

from ......core.check import checked

from ....items.block import BlockItem

from ..host import asDiagramView

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....items.segment import SegmentItem


class DiagramViewApiPlaceMixin:
    @checked
    def placeLine(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.statePlaceLine1)

    @checked
    def placeRectangle(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.statePlaceRectangle1)

    @checked
    def placeEllipse(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.statePlaceEllipse1)

    @checked
    def placePolyline(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.statePlacePolyline1)

    @checked
    def placeText(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.statePlaceText)

    @checked
    def placePort(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.statePlacePort)

    @checked
    def placeGate(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.statePlaceGate)

    @checked
    def placeBlock(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.statePlaceBlock1)

    @checked
    def placeBlockPin(
        self  : Self,
        block : BlockItem | None = None
    ) -> None:
        host = asDiagramView(self)
        if block is None:
            selected = host._selectedItems(BlockItem)
            if len(selected) == 1 and isinstance(selected[0], BlockItem):
                block = selected[0]
        if not isinstance(block, BlockItem):
            logger().warning("No block selected")
            return
        host.state.go(host.statePlaceBlockPin, block)

    @checked
    def placeSymbolPin(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.statePlaceSymbolPin)

    @checked
    def placeConnection(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.statePlaceConn1)

    @checked
    def placeTap(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.statePlaceTap)

    @checked
    def placeNetLabel(self : Self) -> None:
        host = asDiagramView(self)
        host.state.go(host.statePlaceNetLabel)

    @checked
    def placeNetLabelOnSegment(
        self    : Self,
        segment : SegmentItem,
        spos    : QPointF | None = None
    ) -> None:
        host = asDiagramView(self)
        if spos is None:
            spos = segment.sceneMidpoint()
        host._mouse_spos = spos
        host.state.go(host.statePlaceNetLabelOnSegment, [segment])
