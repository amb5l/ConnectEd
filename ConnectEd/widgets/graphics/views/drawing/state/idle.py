from typing import Self

from PyQt6.QtCore import Qt, QPoint, QPointF

from ....items import ItemMixin

from ....items.grip import Grip, ResizeGrip

from ..interaction.edit  import EditMoveInteraction,          \
                                EditMoveBlockPinsInteraction, \
                                EditDuplicateInteraction

from .base import qkm, DrawingViewStateBase


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
            if isinstance(item, Grip):
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
                EditMoveInteraction(self.view, grip, grip.scenePos()),
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
                        EditDuplicateInteraction(self.view, items, self._snap(s)),
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
                    EditMoveBlockPinsInteraction(self.view, pins[0].parentItem(), pins),
                    self.view.stateEditMovePins
                )
            else:
                # other move scenarios
                # TODO filter out pins and child items?
                slide = not(m & qkm.AltModifier)
                self.interact(
                    EditMoveInteraction(self.view, items, self._snap(s), slide),
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
