from typing import Self
from types  import NoneType

from PyQt6.QtCore import Qt, QPoint, QPointF

from .....app import logger, window

from ....dialogs.properties    import PropertiesDialog
from ....dialogs.appearance    import AppearanceDialog
from ....dialogs.text          import TextDialog
from ....dialogs.text_block    import TextBlockDialog
from ....dialogs.property_text import PropertyTextDialog
from ....dialogs.port_pin      import PortPinDialog

from ...items import SignalDirection, ItemMixin

from ...items.handle        import Handle
from ...items.grip          import ResizeGrip
from ...items.block         import Block
from ...items.text          import Text
from ...items.text_block    import TextBlock
from ...items.property_text import PropertyText
from ...items.port          import Port
from ...items.block_pin     import BlockPin
from ...items.symbol_pin    import SymbolPin

from ...scenes.drawing import DrawingScene

from .interaction       import Interaction
from .interaction.edit import  EditMoveInteraction,          \
                               EditMoveBlockPinsInteraction, \
                               EditPasteInteraction,         \
                               EditDuplicateInteraction
from .interaction.place import PlacePortInteraction,         \
                               PlaceBlockInteraction,        \
                               PlaceBlockPinInteraction,     \
                               PlaceSymbolPinInteraction,    \
                               PlaceLineInteraction,         \
                               PlaceRectangleInteraction,    \
                               PlaceEllipseInteraction,      \
                               PlacePolylineInteraction,     \
                               PlaceTextInteraction,         \
                               PlaceTextBlockInteraction,    \
                               PlaceConnInteraction

from ...scenes.drawing.cmd.edit import CmdEditPortPin,     \
                                       CmdEditText,        \
                                       CmdEditPropertyText

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingView


qkm = Qt.KeyboardModifier


class DrawingViewStateBase:
    # instance attributes
    view   : "DrawingView"
    scene  : "DrawingScene"

    def __init__(self : Self, view : "DrawingView") -> None:
        self.view = view
        self.scene = view.scene()

    def go(
        self  : Self,
        state : "DrawingViewStateBase",
        items : list[ItemMixin] | None = None
    ) -> None:
        if state == self.view.stateIdle:
            self.view.interaction = None
        self.view.state = state
        if window() is not None:
            window().status_bar.status.setText(state.STATUS)
        state.entry(
            self.view.mouse.current.physical,
            self.view.mouse.current.logical,
            items
        )

    def interact(
        self        : Self,
        interaction : Interaction,
        state       : "DrawingViewStateBase | None" = None
    ) -> None:
        if interaction.valid:
            self.view.interaction = interaction
            if state is not None:
                self.go(state)
        else:
            self.view.state.go(self.view.stateIdle)

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        pass

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseLeftDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseLeftDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseLeftDoubleClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseMiddleClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseMiddleDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseMiddleDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseMiddleDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def _snap(self : Self, s : QPointF) -> QPointF:
        return self.view._snap(s)


class ClickMixin(DrawingViewStateBase):
    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        if self.view.interaction is not None:
            if self.view.interaction.commit(self._snap(s)):
                self.view.state.go(self.view.stateIdle)

    def mouseLeftDoubleClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        if self.view.interaction is not None:
            self.view.interaction.complete(self._snap(s))
            self.view.state.go(self.view.stateIdle)

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        if self.view.interaction is not None:
            self.view.interaction.update(self._snap(s))


class DragMixin(DrawingViewStateBase):
    def mouseLeftDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        if self.view.interaction is not None:
            self.view.interaction.update(self._snap(s))

    def mouseLeftDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        if self.view.interaction is not None:
            if self.view.interaction.commit(self._snap(s)):
                self.view.state.go(self.view.stateIdle)


class DrawingViewStateIdle(DrawingViewStateBase):
    STATUS = "Idle"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        self.view.interaction = None

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        items = self.view._itemsAt(s)
        for item in items:
            if isinstance(item, Handle):
                return
        if m == qkm.NoModifier:
            if not items or not items[0].isSelected():
                self.scene.clearSelection()
        self.view._selectPoint(s, m)

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        raw_items_at = self.view._itemsAt(s)
        resize_grips_at = \
            [item for item in raw_items_at if isinstance(item, ResizeGrip)]
        # resizing
        if len(resize_grips_at) == 1 and not (m & qkm.AltModifier):
            # handle dragging => resize
            grip = resize_grips_at[0]
            self.interact(
                EditMoveInteraction(self.scene, grip, grip.scenePos()),
                self.view.stateEditResize
            )
            return
        # Check for CTRL+drag duplication when starting on an item
        if (m & qkm.ControlModifier) and raw_items_at:
            # Add item under cursor to selection if not already selected
            item_at = \
                [item for item in raw_items_at if isinstance(item, ItemMixin)]
            if item_at:
                item = item_at[0]  # Get first item under cursor
                if not item.isSelected():
                    item.setSelected(True)
                # Get all currently selected items for duplication
                items = self.view._selectedItems(ItemMixin)
                if items:
                    # Pass the press position for CTRL+drag duplication
                    self.interact(
                        EditDuplicateInteraction(self.scene, items, self._snap(s)),
                        self.view.stateEditDuplicate
                    )
                    return
        if not raw_items_at \
            and not (m & (qkm.ControlModifier | qkm.ShiftModifier)):
            self.scene.clearSelection()
            items = []
        self.view._selectPoint(s, m)
        items = self.scene.selectedItems()
        if items: # slide/move
            pins = self.view._siblingBlockPins(items)
            if pins:
                # move pins
                self.interact(
                    EditMoveBlockPinsInteraction(self.scene, pins[0].parentItem(), pins),
                    self.view.stateEditMovePins
                )
            else:
                # other move scenarios
                # TODO filter out pins and child items?
                slide = not(m & qkm.AltModifier)
                self.interact(
                    EditMoveInteraction(self.scene, items, self._snap(s), slide),
                    self.view.stateEditSlide if slide else self.view.stateEditMove
                )
        else: # start marquee selection
            self.view.marquee.begin(v)
            self.view.state.go(self.view.stateEditSelectArea2)

    def mouseMiddleDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        if m == qkm.NoModifier:
            self.view.pan = v
            self.view.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.view.state.go(self.view.stateViewPan2)
        elif m & qkm.ControlModifier:
            self.view.marquee.begin(v)
            self.view.state.go(self.view.stateViewZoomArea2)


class DrawingViewStateViewPan1(DrawingViewStateBase):
    STATUS = "Pan: pick the first point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.pan = v
        self.view.setCursor(Qt.CursorShape.ClosedHandCursor)
        self.view.state.go(self.view.stateViewPan2)


class DrawingViewStateViewPan2(DrawingViewStateBase):
    STATUS = "Pan: pick the second point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        delta = v - self.view.pan
        self.view.horizontalScrollBar().setValue(
            self.view.horizontalScrollBar().value() - delta.x()
        )
        self.view.verticalScrollBar().setValue(
            self.view.verticalScrollBar().value() - delta.y()
        )
        self.view.pan = None
        self.view.setCursor(Qt.CursorShape.ArrowCursor)
        self.view.state.go(self.view.stateIdle)

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        delta = v - self.view.pan
        self.view.horizontalScrollBar().setValue(
            self.view.horizontalScrollBar().value() - delta.x()
        )
        self.view.verticalScrollBar().setValue(
            self.view.verticalScrollBar().value() - delta.y()
        )
        self.view.pan = v

    def mouseLeftDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseMove(v, s, m)

    def mouseLeftDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)

    def mouseMiddleDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseMove(v, s, m)

    def mouseMiddleDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStateViewZoomArea1(DrawingViewStateBase):
    STATUS = "Zoom Window: pick the first point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.marquee.begin(v)
        self.view.state.go(self.view.stateViewZoomArea2)

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStateViewZoomArea2(DrawingViewStateBase):
    STATUS = "Zoom Window: pick the second point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.marquee.end(v)
        self.view._zoomRect(self.view.marquee.rect())
        self.view.state.go(self.view.stateIdle)

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.marquee.resize(v)

    def mouseLeftDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseMove(v, s, m)

    def mouseLeftDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)

    def mouseMiddleDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseMove(v, s, m)

    def mouseMiddleDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStateEditSelectArea1(DrawingViewStateBase):
    STATUS = "Select: pick the first point of the marquee"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.marquee.begin(v)
        self.view.state.go(self.view.stateEditSelectArea2)

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStateEditSelectArea2(DrawingViewStateBase):
    STATUS = "Select: complete the marquee selection"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.marquee.end(v)
        self.view._selectRect(self.view.marquee.rect(), m & qkm.ControlModifier)
        self.view.state.go(self.view.stateIdle)

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.marquee.resize(v)

    def mouseLeftDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseMove(v, s, m)

    def mouseLeftDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)


class DrawingViewStateEditPaste(ClickMixin):
    STATUS = "Paste: select the paste position"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        self.view.state.interact(EditPasteInteraction(self.scene, self._snap(s)))


class DrawingViewStateEditDuplicate(ClickMixin, DragMixin):
    STATUS = "Duplicate: place the duplicated item(s) as required"


class DrawingViewStateEditSlide(ClickMixin, DragMixin):
    STATUS = "Slide: position the selected item(s) as required"
    SLIDE = True


class DrawingViewStateEditMove(DrawingViewStateEditSlide):
    STATUS = "Move: position the selected item(s) as required"
    SLIDE = False


class DrawingViewStateEditResize(ClickMixin, DragMixin):
    STATUS = "Resize: position the selected handle as required"


class DrawingViewStateEditMovePins(DrawingViewStateBase):
    STATUS = "Move Pins: position the selected pin(s) as required"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        g = self.view.grid
        self.view.interaction.commit(s, g.pitch if g.snap else None)
        self.view.state.go(self.view.stateIdle)

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        g = self.view.grid
        self.view.interaction.update(s, g.pitch if g.snap else None)

    def mouseLeftDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        g = self.view.grid
        self.view.interaction.update(s, g.pitch if g.snap else None)

    def mouseLeftDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        g = self.view.grid
        self.view.interaction.commit(s, g.pitch if g.snap else None)
        self.view.state.go(self.view.stateIdle)


class DrawingViewStateEditAppearance(DrawingViewStateBase):
    STATUS = "Appearance: specify changes"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        items = i or self.view._selectedItems(ItemMixin)
        if items:
            dialog = AppearanceDialog(items, self.view)
            if dialog.exec():
                self.scene.editAppearance(items, dialog.getChoice())
        else:
            logger().warning("No items selected")
        self.view.state.go(self.view.stateIdle)


class DrawingViewStateEditProperties(DrawingViewStateBase):
    STATUS = "Properties: specify changes"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        item = i[0] if i else self.view._selectedItem(ItemMixin)
        if item:
            dialog = PropertiesDialog(item, self.view)
            if dialog.exec():
                self.scene.editProperties(item, dialog.getChanges())
        else:
            logger().warning("No items selected")
        self.view.state.go(self.view.stateIdle)


class DrawingViewStateEditQuery(DrawingViewStateBase):
    STATUS = "Query: pick an item"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view._selectPoint(s, m)
        self.view.editQuery()


class DrawingViewStateEditPort(DrawingViewStateBase):
    STATUS = "Edit Port: specify changes"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        item = i[0] if i else self.view._selectedItem(Port)
        if item:
            dialog = PortPinDialog("Port", item, self.view)
            if dialog.exec():
                name = dialog.getName()
                direction = dialog.getDirection()
                range = dialog.getRange()
                self.scene.undo_stack.push(CmdEditPortPin(
                    self.scene, item, name, direction, range
                ))
        else:
            logger().warning("No port selected")
        self.view.state.go(self.view.stateIdle)


class DrawingViewStateEditBlockPin(DrawingViewStateBase):
    STATUS = "Edit Block Pin: specify changes"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        item = i[0] if i else self.view._selectedItem(BlockPin)
        if item and isinstance(item, BlockPin):
            dialog = PortPinDialog("Block Pin", item, self.view)
            if dialog.exec():
                name = dialog.getName()
                direction = dialog.getDirection()
                range = dialog.getRange()
                self.scene.undo_stack.push(CmdEditPortPin(
                    self.scene, item, name, direction, range
                ))
        else:
            logger().warning("No block pin selected")
        self.view.state.go(self.view.stateIdle)


class DrawingViewStateEditText(DrawingViewStateBase):
    STATUS = "Edit Text: specify changes"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        item = i[0] if i else self.view._selectedItem(Text)
        if item and isinstance(item, Text):
            dialog = TextDialog(item, self.view)
            if dialog.exec():
                text, appearance = dialog.getChoice()
                self.scene.undo_stack.push(CmdEditText(
                    self.scene, item, text, appearance
                ))
        else:
            logger().warning("No text selected")
        self.view.state.go(self.view.stateIdle)


class DrawingViewStateEditPropertyText(DrawingViewStateBase):
    STATUS = "Edit Property Text: specify changes"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        item = i[0] if i else self.view._selectedItem(PropertyText)
        if item and isinstance(item, PropertyText):
            dialog = PropertyTextDialog(item, self.view)
            if dialog.exec():
                name = dialog.getName()
                value = dialog.getValue()
                display = dialog.getDisplay()
                appearance = dialog.getAppearanceChange()
                self.scene.undo_stack.push(CmdEditPropertyText(
                    self.scene, item, name, value, display, appearance
                ))
        else:
            logger().warning("No property text selected")
        self.view.state.go(self.view.stateIdle)


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
                PlacePortInteraction(self.scene, self._snap(s), item)
            )
        else:
            self.view.state.go(self.view.stateIdle)


class DrawingViewStatePlaceBlock1(DrawingViewStateBase):
    STATUS = "Place Block: pick the first point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.interact(
            PlaceBlockInteraction(self.scene, self._snap(s)),
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
                    self.scene, block, pin, self._snap(s),
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
            self.interact(PlaceSymbolPinInteraction(
                self.scene, self._snap(s), pin
            ))
        else:
            self.view.state.go(self.view.stateIdle)


class DrawingViewStatePlaceLine1(ClickMixin):
    STATUS = "Place Line: pick the first point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.interact(
            PlaceLineInteraction(self.scene, self._snap(s)),
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
            PlaceRectangleInteraction(self.scene, self._snap(s)),
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
            PlaceEllipseInteraction(self.scene, self._snap(s)),
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
            PlacePolylineInteraction(self.scene, self._snap(s)),
            self.view.statePlaceEllipse2
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
            self.interact(PlaceTextInteraction(
                self.scene, self._snap(s), item)
            )
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
            self.interact(PlaceTextBlockInteraction(
                self.scene, self._snap(s), item)
            )
        else:
            self.view.state.go(self.view.stateIdle)


class DrawingViewStatePlaceConn1(ClickMixin):
    STATUS = "Place Connection: pick a starting position"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.interact(
            PlaceConnInteraction(self.scene, self._snap(s)),
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


class DrawingViewStateMixin:
    state                 : DrawingViewStateBase
    stateIdle             : DrawingViewStateIdle
    stateViewPan1         : DrawingViewStateViewPan1
    stateViewPan2         : DrawingViewStateViewPan2
    stateViewZoomArea1    : DrawingViewStateViewZoomArea1
    stateViewZoomArea2    : DrawingViewStateViewZoomArea2
    stateEditSelectArea1  : DrawingViewStateEditSelectArea1
    stateEditSelectArea2  : DrawingViewStateEditSelectArea2
    stateEditPaste        : DrawingViewStateEditPaste
    stateEditDuplicate    : DrawingViewStateEditDuplicate
    stateEditSlide        : DrawingViewStateEditSlide
    stateEditMove         : DrawingViewStateEditMove
    stateEditResize       : DrawingViewStateEditResize
    stateEditMovePins     : DrawingViewStateEditMovePins
    stateEditAppearance   : DrawingViewStateEditAppearance
    stateEditProperties   : DrawingViewStateEditProperties
    stateEditQuery        : DrawingViewStateEditQuery
    stateEditPort         : DrawingViewStateEditPort
    stateEditBlockPin     : DrawingViewStateEditBlockPin
    stateEditText         : DrawingViewStateEditText
    stateEditPropertyText : DrawingViewStateEditPropertyText
    statePlacePort        : DrawingViewStatePlacePort
    statePlaceBlock1      : DrawingViewStatePlaceBlock1
    statePlaceBlock2      : DrawingViewStatePlaceBlock2
    statePlaceBlockPin    : DrawingViewStatePlaceBlockPin
    statePlaceSymbolPin   : DrawingViewStatePlaceSymbolPin
    statePlaceRectangle1  : DrawingViewStatePlaceRectangle1
    statePlaceRectangle2  : DrawingViewStatePlaceRectangle2
    statePlaceEllipse1    : DrawingViewStatePlaceEllipse1
    statePlaceEllipse2    : DrawingViewStatePlaceEllipse2
    statePlacePolyline1   : DrawingViewStatePlacePolyline1
    statePlacePolyline2   : DrawingViewStatePlacePolyline2
    statePlaceText        : DrawingViewStatePlaceText
    statePlaceTextBlock   : DrawingViewStatePlaceTextBlock
    statePlaceConn1       : DrawingViewStatePlaceConn1
    statePlaceConn2       : DrawingViewStatePlaceConn2

    def initStates(self : "DrawingView") -> None:
        self.stateIdle             = DrawingViewStateIdle             (self)
        self.stateViewPan1         = DrawingViewStateViewPan1         (self)
        self.stateViewPan2         = DrawingViewStateViewPan2         (self)
        self.stateViewZoomArea1    = DrawingViewStateViewZoomArea1    (self)
        self.stateViewZoomArea2    = DrawingViewStateViewZoomArea2    (self)
        self.stateEditSelectArea1  = DrawingViewStateEditSelectArea1  (self)
        self.stateEditSelectArea2  = DrawingViewStateEditSelectArea2  (self)
        self.stateEditPaste        = DrawingViewStateEditPaste        (self)
        self.stateEditDuplicate    = DrawingViewStateEditDuplicate    (self)
        self.stateEditSlide        = DrawingViewStateEditSlide        (self)
        self.stateEditMove         = DrawingViewStateEditMove         (self)
        self.stateEditResize       = DrawingViewStateEditResize       (self)
        self.stateEditMovePins     = DrawingViewStateEditMovePins     (self)
        self.stateEditAppearance   = DrawingViewStateEditAppearance   (self)
        self.stateEditProperties   = DrawingViewStateEditProperties   (self)
        self.stateEditQuery        = DrawingViewStateEditQuery        (self)
        self.stateEditPort         = DrawingViewStateEditPort         (self)
        self.stateEditBlockPin     = DrawingViewStateEditBlockPin     (self)
        self.stateEditText         = DrawingViewStateEditText         (self)
        self.stateEditPropertyText = DrawingViewStateEditPropertyText (self)
        self.statePlacePort        = DrawingViewStatePlacePort        (self)
        self.statePlaceBlock1      = DrawingViewStatePlaceBlock1      (self)
        self.statePlaceBlock2      = DrawingViewStatePlaceBlock2      (self)
        self.statePlaceBlockPin    = DrawingViewStatePlaceBlockPin    (self)
        self.statePlaceSymbolPin   = DrawingViewStatePlaceSymbolPin   (self)
        self.statePlaceLine1       = DrawingViewStatePlaceLine1       (self)
        self.statePlaceLine2       = DrawingViewStatePlaceLine2       (self)
        self.statePlaceRectangle1  = DrawingViewStatePlaceRectangle1  (self)
        self.statePlaceRectangle2  = DrawingViewStatePlaceRectangle2  (self)
        self.statePlaceEllipse1    = DrawingViewStatePlaceEllipse1    (self)
        self.statePlaceEllipse2    = DrawingViewStatePlaceEllipse2    (self)
        self.statePlacePolyline1   = DrawingViewStatePlacePolyline1   (self)
        self.statePlacePolyline2   = DrawingViewStatePlacePolyline2   (self)
        self.statePlaceText        = DrawingViewStatePlaceText        (self)
        self.statePlaceTextBlock   = DrawingViewStatePlaceTextBlock   (self)
        self.statePlaceConn1       = DrawingViewStatePlaceConn1       (self)
        self.statePlaceConn2       = DrawingViewStatePlaceConn2       (self)
