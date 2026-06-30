from typing          import Self
from collections.abc import Sequence

from PyQt6.QtCore    import QPoint, QPointF
from PyQt6.QtWidgets import QGraphicsItem

from ......core.check import checked

from ......app import logger

from ......core.types import Direction

from .....dialogs.items.text      import TextItemDialog
from .....dialogs.items.port_pin  import PortPinItemDialog
from .....dialogs.items.gate      import GateItemDialog
from .....dialogs.items.net_label import NetLabelItemDialog

from ....items.text       import TextItem
from ....items.port       import PortItem
from ....items.gate       import GateFunc, BufGateItem, \
                                 AndGateItem, OrGateItem, XorGateItem
from ....items.block      import BlockItem
from ....items.block_pin  import BlockPinItem
from ....items.symbol_pin import SymbolPinItem
from ....items.segment    import SegmentItem
from ....items.net_label  import NetLabelItem

from ..mouse import MouseModifier

from .mixin import StartMixin, ClickMixin, DragMixin

from ..interaction.place import (
    DiagramPlaceLineInteraction,
    DiagramPlaceRectangleInteraction,
    DiagramPlaceEllipseInteraction,
    DiagramPlacePolylineInteraction,
    DiagramPlaceTextInteraction,
    DiagramPlacePortInteraction,
    DiagramPlaceGateInteraction,
    DiagramPlaceBlockInteraction,
    DiagramPlaceBlockPinInteraction,
    DiagramPlaceSymbolPinInteraction,
    DiagramPlaceConnInteraction,
    DiagramPlaceTapInteraction,
    DiagramPlaceNetLabelInteraction
)

from .base import DiagramViewState


class DiagramViewStatePlaceLine1(StartMixin, ClickMixin, DiagramViewState):
    STATUS = "Place Line: pick the first point"

    _INTERACTION_CLS = DiagramPlaceLineInteraction

    def _nextState(self : Self) -> DiagramViewState:
        return self.view.statePlaceLine2

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self._start(self.view._snap(spos))

    def mouseLeftDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.mouseLeftClick(vpos, spos, modifiers)


class DiagramViewStatePlaceLine2(ClickMixin, DragMixin, DiagramViewState):
    STATUS = "Place Line: pick the second point"


class DiagramViewStatePlaceRectangle1(StartMixin, DiagramViewState):
    STATUS = "Place Rectangle: pick the first point"

    _INTERACTION_CLS = DiagramPlaceRectangleInteraction

    def _nextState(self : Self) -> DiagramViewState:
        return self.view.statePlaceRectangle2

    def mouseLeftClick(
        self : Self,
        vpos : QPoint,
        spos : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self._start(self.view._snap(spos))

    def mouseLeftDragBegin(
        self : Self,
        vpos : QPoint,
        spos : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.mouseLeftClick(vpos, spos, modifiers)


class DiagramViewStatePlaceRectangle2(ClickMixin, DragMixin, DiagramViewState):
    STATUS = "Place Rectangle: pick the second point"


class DiagramViewStatePlaceEllipse1(StartMixin, DiagramViewState):
    STATUS = "Place Ellipse: pick the first point"

    _INTERACTION_CLS = DiagramPlaceEllipseInteraction

    def _nextState(self : Self) -> DiagramViewState:
        return self.view.statePlaceEllipse2

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self._start(self.view._snap(spos))

    def mouseLeftDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.mouseLeftClick(vpos, spos, modifiers)


class DiagramViewStatePlaceEllipse2(ClickMixin, DragMixin, DiagramViewState):
    STATUS = "Place Ellipse: pick the second point"


class DiagramViewStatePlacePolyline1(StartMixin, DiagramViewState):
    STATUS = "Place Polyline: pick the first point"

    _INTERACTION_CLS = DiagramPlacePolylineInteraction

    def _nextState(self : Self) -> DiagramViewState:
        return self.view.statePlacePolyline2

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self._start(self.view._snap(spos))

    def mouseLeftDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.mouseLeftClick(vpos, spos, modifiers)


class DiagramViewStatePlacePolyline2(ClickMixin, DragMixin, DiagramViewState):
    STATUS = "Place Polyline: pick the next point"


class DiagramViewStatePlaceText(ClickMixin, DiagramViewState):
    STATUS = "Place Text: pick a position"

    @checked
    def entry(
        self : Self,
        items : Sequence[QGraphicsItem],
        spos  : QPointF | None = None
    ) -> None:
        spos = self._requireNoItemsSpos(items, spos)
        item = TextItem(pos=self.view._snap(spos))
        dialog = TextItemDialog(item, self.view)
        if dialog.exec():
            item.applyDialog(dialog)
            self.interact(DiagramPlaceTextInteraction(
                self.view, self.view._snap(spos), item)
            )
        else:
            self.view.state.go(self.view.stateIdle)


class DiagramViewStatePlacePort(ClickMixin, DiagramViewState):
    STATUS = "Place Port: pick a location"

    @checked
    def entry(
        self : Self,
        items : Sequence[QGraphicsItem],
        spos  : QPointF | None = None
    ) -> None:
        spos = self._requireNoItemsSpos(items, spos)
        item = PortItem()
        item.setPos(self.view._snap(spos))
        dialog = PortPinItemDialog("Port", item, self.view)
        if dialog.exec():
            item.setName(dialog.getName())
            item.setDirection(dialog.getDirection())
            item.setRotation(
                180 if dialog.getDirection() == Direction.IN else 0
            )
            self.interact(
                DiagramPlacePortInteraction(self.view, self.view._snap(spos), item)
            )
        else:
            self.view.state.go(self.view.stateIdle)


class DiagramViewStatePlaceGate(ClickMixin, DiagramViewState):
    STATUS = "Place Gate: pick a location"

    @checked
    def entry(
        self  : Self,
        items : Sequence[QGraphicsItem],
        spos  : QPointF | None = None
    ) -> None:
        spos = self._requireNoItemsSpos(items, spos)
        dialog = GateItemDialog(self.view)
        if dialog.exec():
            match dialog.getFunction():
                case GateFunc.BUF_INV  : gate = BufGateItem()
                case GateFunc.AND_NAND : gate = AndGateItem(dialog.getWidth())
                case GateFunc.OR_NOR   : gate = OrGateItem(dialog.getWidth())
                case GateFunc.XOR_XNOR : gate = XorGateItem(dialog.getWidth())
            gate.setPos(self.view._snap(spos))
            self.interact(DiagramPlaceGateInteraction(
                self.view, self.view._snap(spos), gate
            ))
        else:
            self.view.state.go(self.view.stateIdle)


class DiagramViewStatePlaceBlock1(StartMixin, DiagramViewState):
    STATUS = "Place Block: pick the first point"

    _INTERACTION_CLS = DiagramPlaceBlockInteraction

    def _nextState(self : Self) -> DiagramViewState:
        return self.view.statePlaceBlock2

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self._start(self.view._snap(spos))

    def mouseLeftDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.mouseLeftClick(vpos, spos, modifiers)


class DiagramViewStatePlaceBlock2(ClickMixin, DragMixin, DiagramViewState):
    STATUS = "Place Block: pick the second point"


class DiagramViewStatePlaceBlockPin(DiagramViewState):
    STATUS = "Place Block Pin: pick a location"

    @checked
    def entry(
        self  : Self,
        items : Sequence[QGraphicsItem],
        spos  : QPointF | None = None
    ) -> None:
        block, spos = self._requireOneItemSpos(items, spos)
        if isinstance(block, BlockItem):
            pin = BlockPinItem() # don't parent to block yet
            dialog = PortPinItemDialog("Block Pin", pin, self.view)
            if dialog.exec():
                pin.setName(dialog.getName())
                pin.setDirection(dialog.getDirection())
                self.interact(DiagramPlaceBlockPinInteraction(
                    self.view, block, pin, self.view._snap(spos),
                    self.view.grid.pitch if self.view.grid.snap else None
                ))
        else:
            logger().warning("No pin rect selected")
            self.view.state.go(self.view.stateIdle)

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self._interaction().commit(
            self.view._snap(spos),
            self.view.grid.pitch if self.view.grid.snap else None
        )
        self.view.state.go(self.view.stateIdle)

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self._interaction().update(
            self.view._snap(spos),
            self.view.grid.pitch if self.view.grid.snap else None
        )

class DiagramViewStatePlaceSymbolPin(ClickMixin, DiagramViewState):
    STATUS = "Place Symbol Pin: pick a location"

    @checked
    def entry(
        self : Self,
        items : Sequence[QGraphicsItem],
        spos  : QPointF | None = None
    ) -> None:
        spos = self._requireNoItemsSpos(items, spos)
        pin = SymbolPinItem()
        pin.setPos(self.view._snap(spos))
        dialog = PortPinItemDialog("Pin", pin, self.view)
        if dialog.exec():
            pin.setName(dialog.getName())
            pin.setDirection(dialog.getDirection())
            self.interact(DiagramPlaceSymbolPinInteraction(
                self.view, self.view._snap(spos), pin
            ))
        else:
            self.view.state.go(self.view.stateIdle)


class DiagramViewStatePlaceConn1(StartMixin, ClickMixin, DiagramViewState):
    STATUS = "Place Connection: pick a starting position"

    _INTERACTION_CLS = DiagramPlaceConnInteraction

    def _nextState(self : Self) -> DiagramViewState:
        return self.view.statePlaceConn2

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self._start(self.view._snap(spos))

    def mouseLeftDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.mouseLeftClick(vpos, spos, modifiers)


class DiagramViewStatePlaceConn2(ClickMixin, DiagramViewState):
    STATUS = "Place Connection: place a mid- or end-point"

    def mouseLeftDoubleClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        if not self._interaction().commit(self.view._snap(spos)):
            self._interaction().cancel()
        self.view.state.go(self.view.statePlaceConn1)

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        if self._interaction().commit(self.view._snap(spos)):
            self.view.state.go(self.view.statePlaceConn1)

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self._interaction().update(self.view._snap(spos))

    def mouseLeftDragCont(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.mouseMove(vpos, spos, modifiers)

    def mouseLeftDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        if self._interaction().commit(self.view._snap(spos)):
            self.view.state.go(self.view.statePlaceConn1)


class DiagramViewStatePlaceTap(ClickMixin, DiagramViewState):
    STATUS = "Place Tap: pick a location"

    @checked
    def entry(
        self : Self,
        items : Sequence[QGraphicsItem],
        spos  : QPointF | None = None
    ) -> None:
        spos = self._requireNoItemsSpos(items, spos)
        self._interact(spos)

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self._commit(spos)
        self._interact(spos)

    def _interact(self : Self, spos : QPointF) -> None:
        self.interact(DiagramPlaceTapInteraction(
            self.view, self.view._snap(spos)
        ))


class DiagramViewStatePlaceNetLabel(ClickMixin, DiagramViewState):
    STATUS = "Place Net Label: pick a position"

    @checked
    def entry(
        self : Self,
        items : Sequence[QGraphicsItem],
        spos  : QPointF | None = None
    ) -> None:
        spos = self._requireNoItemsSpos(items, spos)
        item = NetLabelItem(name="Name", pos=self.view._snap(spos))
        dialog = NetLabelItemDialog(item, self.view)
        if dialog.exec():
            item.applyDialog(dialog)
            self.interact(DiagramPlaceNetLabelInteraction(
                self.view, self.view._snap(spos), item
            ))
        else:
            self.view.state.go(self.view.stateIdle)


class DiagramViewStatePlaceNetLabelOnSegment(ClickMixin, DiagramViewState):
    STATUS = "Place Net Label on Connection: edit details"

    @checked
    def entry(
        self : Self,
        items : Sequence[QGraphicsItem],
        spos  : QPointF | None = None
    ) -> None:
        segment = self._requireOneItem(items)
        if isinstance(segment, SegmentItem):
            snap   = segment.sceneMidpoint() if spos is None \
                     else self.view._snap(spos)
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
