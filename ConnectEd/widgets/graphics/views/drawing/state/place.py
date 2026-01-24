from typing import Self
from types  import NoneType

from PyQt6.QtCore import QPoint, QPointF

from ......app import logger

from .....dialogs.port_pin import PortPinDialog
from .....dialogs.gate     import GateDialog
from .....dialogs.text     import TextItemDialog

from ....items            import SignalDirection, ItemMixin
from ....items.port       import PortItem
from ....items.gate       import GateFunc, BufGateItem, AndGateItem, OrGateItem, XorGateItem
from ....items.block      import BlockItem
from ....items.block_pin  import BlockPinItem
from ....items.symbol_pin import SymbolPinItem
from ....items.text       import TextItem

from ..interaction.place import PlacePortInteraction, \
                                PlaceGateInteraction, \
                                PlaceBlockInteraction, \
                                PlaceBlockPinInteraction, \
                                PlaceSymbolPinInteraction, \
                                PlaceLineInteraction, \
                                PlaceRectangleInteraction, \
                                PlaceEllipseInteraction, \
                                PlacePolylineInteraction, \
                                PlaceTextInteraction, \
                                PlaceConnInteraction

from .base  import qkm, DrawingViewStateBase
from .mixin import ClickMixin, DragMixin


class DrawingViewStatePlacePort(ClickMixin, DrawingViewStateBase):
    STATUS = "Place Port: pick a location"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        item = PortItem()
        item.setPos(self._snap(s))
        dialog = PortPinDialog("Port", item, self.view)
        if dialog.exec():
            item.setName(dialog.getName())
            item.setDirection(dialog.getDirection())
            item.setRotation(
                180 if dialog.getDirection() == SignalDirection.IN else 0
            )
            self.interact(
                PlacePortInteraction(self.view, self._snap(s), item)
            )
        else:
            self.view.state.go(self.view.stateIdle)


class DrawingViewStatePlaceGate(ClickMixin, DrawingViewStateBase):
    STATUS = "Place Gate: pick a location"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        dialog = GateDialog(self.view)
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


class DrawingViewStatePlaceBlock1(DrawingViewStateBase):
    STATUS = "Place Block: pick the first point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.interact(
            PlaceBlockInteraction(self.view, self._snap(s)),
            self.view.statePlaceBlock2
        )

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStatePlaceBlock2(ClickMixin, DragMixin, DrawingViewStateBase):
    STATUS = "Place Block: pick the second point"


class DrawingViewStatePlaceBlockPin(DrawingViewStateBase):
    STATUS = "Place Block Pin: pick a location"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        block = i[0] if i else self.view._selectedItem(BlockItem)
        if block and isinstance(block, BlockItem):
            pin = BlockPinItem() # don't parent to block yet
            dialog = PortPinDialog("Block Pin", pin, self.view)
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


class DrawingViewStatePlaceSymbolPin(ClickMixin, DrawingViewStateBase):
    STATUS = "Place Symbol Pin: pick a location"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : NoneType = None  # not used
    ) -> None:
        pin = SymbolPinItem()
        pin.setPos(self._snap(s))
        dialog = PortPinDialog("Pin", pin, self.view)
        if dialog.exec():
            pin.setName(dialog.getName())
            pin.setDirection(dialog.getDirection())
            self.interact(PlaceSymbolPinInteraction(self.view, self._snap(s), pin))
        else:
            self.view.state.go(self.view.stateIdle)


class DrawingViewStatePlaceLine1(ClickMixin, DrawingViewStateBase):
    STATUS = "Place Line: pick the first point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.interact(
            PlaceLineInteraction(self.view, self._snap(s)),
            self.view.statePlaceLine2
        )

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStatePlaceLine2(ClickMixin, DragMixin, DrawingViewStateBase):
    STATUS = "Place Line: pick the second point"


class DrawingViewStatePlaceRectangle1(DrawingViewStateBase):
    STATUS = "Place Rectangle: pick the first point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.interact(
            PlaceRectangleInteraction(self.view, self._snap(s)),
            self.view.statePlaceRectangle2
        )

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStatePlaceRectangle2(ClickMixin, DragMixin, DrawingViewStateBase):
    STATUS = "Place Rectangle: pick the second point"


class DrawingViewStatePlaceEllipse1(DrawingViewStateBase):
    STATUS = "Place Ellipse: pick the first point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.interact(
            PlaceEllipseInteraction(self.view, self._snap(s)),
            self.view.statePlaceEllipse2
        )

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStatePlaceEllipse2(ClickMixin, DragMixin, DrawingViewStateBase):
    STATUS = "Place Ellipse: pick the second point"


class DrawingViewStatePlacePolyline1(DrawingViewStateBase):
    STATUS = "Place Polyline: pick the first point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.interact(
            PlacePolylineInteraction(self.view, self._snap(s)),
            self.view.statePlacePolyline2
        )

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStatePlacePolyline2(ClickMixin, DragMixin, DrawingViewStateBase):
    STATUS = "Place Polyline: pick the next point"


class DrawingViewStatePlaceText(ClickMixin, DrawingViewStateBase):
    STATUS = "Place Text: pick a position"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        item = TextItem(self._snap(s))
        dialog = TextItemDialog(item, self.view)
        if dialog.exec():
            item.setText(dialog.getText())
            item.setBlock(dialog.getBlock())
            item.setAlignH(dialog.getAlignH())
            item.setAlignV(dialog.getAlignV())
            item.setQuillColor(dialog.getColor())
            item.setQuillFamily(dialog.getFamily())
            item.setQuillSize(dialog.getSize())
            item.setQuillBold(dialog.getBold())
            item.setQuillItalic(dialog.getItalic())
            item.setQuillUnderline(dialog.getUnderline())
            self.interact(PlaceTextInteraction(self.view, self._snap(s), item))
        else:
            self.view.state.go(self.view.stateIdle)


class DrawingViewStatePlaceConn1(ClickMixin, DrawingViewStateBase):
    STATUS = "Place Connection: pick a starting position"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.interact(
            PlaceConnInteraction(self.view, self._snap(s)),
            self.view.statePlaceConn2
        )

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStatePlaceConn2(ClickMixin, DrawingViewStateBase):
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
