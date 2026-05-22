from typing import Self

from PyQt6.QtCore import QPoint, QPointF

from ......core.check import checked

from ......app import logger

from ......core.types import Direction, NO_CHANGE

from .....dialogs.items.port_pin  import PortPinItemDialog
from .....dialogs.items.gate      import GateItemDialog
from .....dialogs.items.net_label import NetLabelItemDialog

from ....items.mixin      import ItemMixin
from ....items.port       import PortItem
from ....items.gate       import GateFunc, BufGateItem, \
                                 AndGateItem, OrGateItem, XorGateItem
from ....items.block      import BlockItem
from ....items.block_pin  import BlockPinItem
from ....items.segment    import SegmentItem
from ....items.net_label  import NetLabelItem

from ...drawing.state.base import qkm

from ...drawing.state.mixin import StartMixin, ClickMixin, DragMixin

from ..interaction.place import PlacePortInteraction,     \
                                PlaceGateInteraction,     \
                                PlaceBlockInteraction,    \
                                PlaceBlockPinInteraction, \
                                PlaceConnInteraction,      \
                                PlaceTapInteraction,       \
                                PlaceNetLabelInteraction

from .base import DiagramViewStateBase


class DiagramViewStatePlacePort(ClickMixin, DiagramViewStateBase):
    STATUS = "Place Port: pick a location"

    @checked
    def entry(
        self : Self,
        v    : QPoint | None,
        s    : QPointF | None,
        i    : list[ItemMixin] | None = None
    ) -> None:
        item = PortItem()
        item.setPos(self._snap(s))
        dialog = PortPinItemDialog("Port", item, self.view)
        if dialog.exec():
            item.setName(dialog.getName())
            item.setDirection(dialog.getDirection())
            item.setRotation(
                180 if dialog.getDirection() == Direction.IN else 0
            )
            self.interact(
                PlacePortInteraction(self.view, self._snap(s), item)
            )
        else:
            self.view.state.go(self.view.stateIdle)


class DiagramViewStatePlaceGate(ClickMixin, DiagramViewStateBase):
    STATUS = "Place Gate: pick a location"

    @checked
    def entry(
        self : Self,
        v    : QPoint | None,
        s    : QPointF | None,
        i    : list[ItemMixin] | None = None
    ) -> None:
        dialog = GateItemDialog(self.view)
        if dialog.exec():
            match dialog.getFunction():
                case GateFunc.BUF_INV  : gate = BufGateItem()
                case GateFunc.AND_NAND : gate = AndGateItem(dialog.getWidth())
                case GateFunc.OR_NOR   : gate = OrGateItem(dialog.getWidth())
                case GateFunc.XOR_XNOR : gate = XorGateItem(dialog.getWidth())
            gate.setPos(self._snap(s))
            self.interact(PlaceGateInteraction(self.view, self._snap(s), gate))
        else:
            self.view.state.go(self.view.stateIdle)


class DiagramViewStatePlaceBlock1(StartMixin, DiagramViewStateBase):
    STATUS = "Place Block: pick the first point"

    _INTERACTION_CLS = PlaceBlockInteraction

    def _nextState(self : Self) -> DiagramViewStateBase:
        return self.view.statePlaceBlock2

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self._start(self._snap(s))

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DiagramViewStatePlaceBlock2(ClickMixin, DragMixin, DiagramViewStateBase):
    STATUS = "Place Block: pick the second point"


class DiagramViewStatePlaceBlockPin(DiagramViewStateBase):
    STATUS = "Place Block Pin: pick a location"

    @checked
    def entry(
        self : Self,
        v    : QPoint | None,
        s    : QPointF | None,
        i    : list[ItemMixin] | None = None
    ) -> None:
        block = i[0] if i else self.view._selectedItem(BlockItem)
        if block and isinstance(block, BlockItem):
            pin = BlockPinItem() # don't parent to block yet
            dialog = PortPinItemDialog("Block Pin", pin, self.view)
            if dialog.exec():
                pin.setName(dialog.getName())
                pin.setDirection(dialog.getDirection())
                self.interact(PlaceBlockPinInteraction(
                    self.view, block, pin, self._snap(s),
                    self.view.grid.pitch if self.view.grid.snap else None
                ))
        else:
            logger().warning("No pin rect selected")
            self.view.state.go(self.view.stateIdle)

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.interaction.commit(
            self._snap(s),
            self.view.grid.pitch if self.view.grid.snap else None
        )
        self.view.state.go(self.view.stateIdle)

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.interaction.update(
            self._snap(s),
            self.view.grid.pitch if self.view.grid.snap else None
        )

class DiagramViewStatePlaceConn1(StartMixin, ClickMixin, DiagramViewStateBase):
    STATUS = "Place Connection: pick a starting position"

    _INTERACTION_CLS = PlaceConnInteraction

    def _nextState(self : Self) -> DiagramViewStateBase:
        return self.view.statePlaceConn2

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self._start(self._snap(s))

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DiagramViewStatePlaceConn2(ClickMixin, DiagramViewStateBase):
    STATUS = "Place Connection: place a mid- or end-point"

    def mouseLeftDoubleClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        if not self.view.interaction.commit(self._snap(s)):
            self.view.interaction.cancel()
        self.view.state.go(self.view.statePlaceConn1)

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        if self.view.interaction.commit(self._snap(s)):
            self.view.state.go(self.view.statePlaceConn1)

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.interaction.update(self._snap(s))

    def mouseLeftDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseMove(v, s, m)

    def mouseLeftDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        if self.view.interaction.commit(self._snap(s)):
            self.view.state.go(self.view.statePlaceConn1)


class DiagramViewStatePlaceTap(ClickMixin, DiagramViewStateBase):
    STATUS = "Place Tap: pick a location"

    @checked
    def entry(
        self : Self,
        v    : QPoint | None,
        s    : QPointF | None,
        i    : list[ItemMixin] | None = None
    ) -> None:
        self._interact(s)

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self._commit(s)
        self._interact(s)

    def _interact(self : Self, s : QPointF) -> None:
        self.interact(PlaceTapInteraction(self.view, self._snap(s)))


class DiagramViewStatePlaceNetLabel(ClickMixin, DiagramViewStateBase):
    STATUS = "Place Net Label: pick a position"

    @checked
    def entry(
        self : Self,
        v    : QPoint | None,
        s    : QPointF | None,
        i    : list[ItemMixin] | None = None
    ) -> None:
        pos  = self._snap(s)
        item = NetLabelItem(name="Name", pos=pos)
        dialog = NetLabelItemDialog(item, self.view)
        if dialog.exec():
            item.applyDialog(dialog)
            self.interact(
                PlaceNetLabelInteraction(self.view, pos, item)
            )
        else:
            self.view.state.go(self.view.stateIdle)


class DiagramViewStatePlaceNetLabelOnSegment(ClickMixin, DiagramViewStateBase):
    STATUS = "Place Net Label on Connection: edit details"

    @checked
    def entry(
        self : Self,
        v    : QPoint | None,
        s    : QPointF | None,
        i    : list[ItemMixin] | None = None
    ) -> None:
        segment = i[0] if i else self.view._selectedItem(SegmentItem)
        if segment and isinstance(segment, SegmentItem):
            snap   = self._snap(s) if s is not None else segment.sceneMidpoint()
            item   = NetLabelItem(name="Name")
            dialog = NetLabelItemDialog(item, self.view)
            if not dialog.exec():
                self.view.state.go(self.view.stateIdle)
                return
            item.applyDialog(dialog)
            self.scene.addItems([item], undoable=True)
            item.setPos(segment.perpendicularIntersection(snap))
        else:
            logger().warning("No segment selected")
        self.view.state.go(self.view.stateIdle)
