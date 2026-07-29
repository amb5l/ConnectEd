from typing          import Self
from collections.abc import Sequence

from PyQt6.QtCore    import Qt, QPoint, QPointF
from PyQt6.QtWidgets import QGraphicsItem

from ......core.check import checked

from ....items.grip          import GripItem, MoveGripItem, ResizeGripItem
from ....items.polyline      import PolySegItem, PolylineItem
from ....items.text          import TextItem
from ....items.property_text import PropertyTextItem
from ....items.block         import BlockItem

from ....items.mixin         import ItemMixin

from ..mouse import MouseModifier

from ..interaction.edit import (
    EditAdjustPolySegInteraction,
    EditDuplicateInteraction
)
from ..interaction.move import (
    MoveInteraction,
    MoveBlockPinsInteraction,
    MoveGripInteraction
)

from .base import DiagramViewState


class DiagramViewStateIdle(DiagramViewState):
    STATUS = "Idle"

    @checked
    def entry(
        self : Self,
        items : QGraphicsItem | Sequence[QGraphicsItem] | None = None,
        spos  : QPointF | None = None
    ) -> None:
        self.view.interaction = None

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.view._selectClick(spos, modifiers)

    def mouseLeftDoubleClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        items = self.view._itemsAt(spos)
        for item in items:
            if isinstance(item, PropertyTextItem):
                self.view.state.go(
                    self.view.stateEditPropertyText, item
                )
                return
            if isinstance(item, TextItem):
                self.view.state.go(self.view.stateEditText, item)
                return

    def mouseLeftDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        raw_items_at = self.view._itemsAt(spos)
        grips_at : list[GripItem] = []
        top_items_at = []
        for item in raw_items_at:
            if item.parentItem() is None:
                top_items_at.append(item)
            elif isinstance(item, GripItem):
                grips_at.append(item)
        # grips
        if len(grips_at) == 1 and not (modifiers & MouseModifier.ALT):
            # single grip
            grip = grips_at[0]
            if grip.movable():
                if isinstance(grip, PolySegItem):
                    # adjust polyline segment/arc
                    polyline = grip.parentItem()
                    if not isinstance(polyline, PolylineItem):
                        raise RuntimeError("Expected polyline")
                    self.interact(
                        EditAdjustPolySegInteraction(
                            self.view, polyline, grip, grip.scenePos()
                        ),
                        self.view.stateEditAdjustPolySeg
                    )
                elif isinstance(grip, MoveGripItem | ResizeGripItem):
                    self.interact(MoveGripInteraction(
                        self.view, grip, grip.scenePos()
                    ))
            return
        # Check for CTRL+drag duplication when starting on an item
        if (modifiers & MouseModifier.CTRL) and raw_items_at:
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
                        EditDuplicateInteraction(
                            self.view, items, self.view._snap(spos)
                        ),
                        self.view.stateEditDuplicate
                    )
                    return
        if not raw_items_at \
        and not (modifiers & (MouseModifier.CTRL | MouseModifier.SHIFT)):
            self.scene.clearSelection()
            items = []
        self.view._selectDrag(spos, modifiers)
        items = self.scene.selectedItems()
        if items: # slide/move
            pins = self.view._siblingBlockPins(items)
            if pins:
                # move pins
                block = pins[0].parentItem()
                if not isinstance(block, BlockItem):
                    raise RuntimeError("Expected block parent")
                self.interact(
                    MoveBlockPinsInteraction(self.view, block, pins),
                    self.view.stateEditMovePins
                )
            else:
                # other move scenarios
                if items:
                    slide = not(modifiers & MouseModifier.ALT)
                    self.interact(
                        MoveInteraction(
                            self.view, items, self.view._snap(spos), slide
                        ),
                        self.view.stateEditSlide if slide else \
                        self.view.stateEditMove
                    )
        else: # start marquee selection
            self.view.marquee.begin(vpos)
            self.view.state.go(self.view.stateEditSelectArea2)

    def mouseMiddleDragBegin(self : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        if modifiers == MouseModifier.NONE:
            self.view._pan_pos = vpos
            self.view.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.view.state.go(self.view.stateViewPan2)
        elif modifiers & MouseModifier.CTRL:
            self.view.marquee.begin(vpos)
            self.view.state.go(self.view.stateViewZoomArea2)
