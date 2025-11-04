from typing import Self
from types  import NoneType

from PyQt6.QtCore import QPoint, QPointF

from ......app import logger

from .....dialogs.port_pin   import PortPinDialog
from .....dialogs.text       import TextDialog
from .....dialogs.text_block import TextBlockDialog

from ....items            import SignalDirection, ItemMixin
from ....items.port       import Port
from ....items.block      import Block
from ....items.block_pin  import BlockPin
from ....items.symbol_pin import SymbolPin
from ....items.text       import Text
from ....items.text_block import TextBlock

from ..interaction.place import PlacePortInteraction, \
                                PlaceBlockInteraction, \
                                PlaceBlockPinInteraction, \
                                PlaceSymbolPinInteraction, \
                                PlaceLineInteraction, \
                                PlaceRectangleInteraction, \
                                PlaceEllipseInteraction, \
                                PlacePolylineInteraction, \
                                PlaceTextInteraction, \
                                PlaceTextBlockInteraction, \
                                PlaceConnInteraction

from .base  import qkm, DrawingViewStateBase
from .mixin import ClickMixin, DragMixin


class DrawingViewStatePlacePort(ClickMixin):
    STATUS = "Place Port: pick a location"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        item = Port()
        item.setPos(self._snap(s))
        dialog = PortPinDialog("Port", item, self.view)
        if dialog.exec():
            item.name = dialog.getName()
            item.direction = dialog.getDirection()
            item.range = dialog.getRange()
            item.setRotation(
                180 if dialog.getDirection() == SignalDirection.IN else 0
            )
            self.interact(
                PlacePortInteraction(self.view, self._snap(s), item)
            )
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


class DrawingViewStatePlaceBlock2(ClickMixin, DragMixin):
    STATUS = "Place Block: pick the second point"


class DrawingViewStatePlaceBlockPin(DrawingViewStateBase):
    STATUS = "Place Block Pin: pick a location"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        block = i[0] if i else self.view._selectedItem(Block)
        if block and isinstance(block, Block):
            pin = BlockPin() # don't parent to block yet
            dialog = PortPinDialog("Block Pin", pin, self.view)
            if dialog.exec():
                pin.name = dialog.getName()
                pin.direction = dialog.getDirection()
                pin.range = dialog.getRange()
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


class DrawingViewStatePlaceSymbolPin(ClickMixin):
    STATUS = "Place Symbol Pin: pick a location"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : NoneType = None  # not used
    ) -> None:
        pin = SymbolPin()
        pin.setPos(self._snap(s))
        dialog = PortPinDialog("Pin", pin, self.view)
        if dialog.exec():
            pin.name = dialog.getName()
            pin.direction = dialog.getDirection()
            pin.range = dialog.getRange()
            self.interact(PlaceSymbolPinInteraction(self.view, self._snap(s), pin))
        else:
            self.view.state.go(self.view.stateIdle)


class DrawingViewStatePlaceLine1(ClickMixin):
    STATUS = "Place Line: pick the first point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.interact(
            PlaceLineInteraction(self.view, self._snap(s)),
            self.view.statePlaceLine2
        )

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStatePlaceLine2(ClickMixin, DragMixin):
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


class DrawingViewStatePlaceRectangle2(ClickMixin, DragMixin):
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


class DrawingViewStatePlaceEllipse2(ClickMixin, DragMixin):
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


class DrawingViewStatePlacePolyline2(ClickMixin, DragMixin):
    STATUS = "Place Polyline: pick the next point"


class DrawingViewStatePlaceText(ClickMixin):
    STATUS = "Place Text: pick a position"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        item = Text(self._snap(s))
        dialog = TextDialog(item, self.view)
        if dialog.exec():
            text, appearance = dialog.getChoice()
            item.setText(text)
            item.a.quill.setPref(appearance)
            self.interact(PlaceTextInteraction(self.view, self._snap(s), item))
        else:
            self.view.state.go(self.view.stateIdle)


class DrawingViewStatePlaceTextBlock(ClickMixin):
    STATUS = "Place Text Block: pick a position"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        item = TextBlock(self._snap(s))
        dialog = TextBlockDialog(item, self.view)
        if dialog.exec():
            text, appearance = dialog.getChoice()
            item.setPlainText(text)
            item.a.quill.setPref(appearance)
            self.interact(PlaceTextBlockInteraction(self.view, self._snap(s), item))
        else:
            self.view.state.go(self.view.stateIdle)


class DrawingViewStatePlaceConn1(ClickMixin):
    STATUS = "Place Connection: pick a starting position"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.interact(
            PlaceConnInteraction(self.view, self._snap(s)),
            self.view.statePlaceConn2
        )

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStatePlaceConn2(ClickMixin):
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
