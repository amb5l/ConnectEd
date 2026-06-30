from typing          import Self, cast
from collections.abc import Sequence

from PyQt6.QtCore    import QPoint, QPointF
from PyQt6.QtWidgets import QGraphicsItem

from ......app import logger

from ......core.check import checked
from ......core.types import NoChange

from .....dialogs.items.text          import TextItemDialog
from .....dialogs.items.property_text import PropertyTextItemDialog
from .....dialogs.items.port_pin      import PortPinItemDialog
from .....dialogs.appearance          import AppearanceDialog
from .....dialogs.properties          import PropertiesDialog

from ....properties import PropertiesMixin

from ....items.text          import TextItem
from ....items.property_text import PropertyTextItem
from ....items.port          import PortItem
from ....items.block_pin     import BlockPinItem

from ....items.mixin.presentation import ItemPresentationMixin

from ..mouse import MouseModifier

from ..interaction.edit import EditPasteInteraction

from .base  import DiagramViewState
from .mixin import ClickMixin, DragMixin


class DiagramViewStateEditSelectArea1(DiagramViewState):
    STATUS = "Select: pick the first point of the marquee"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.view.marquee.begin(vpos)
        self.view.state.go(self.view.stateEditSelectArea2)

    def mouseLeftDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.mouseLeftClick(vpos, spos, modifiers)


class DiagramViewStateEditSelectArea2(DiagramViewState):
    STATUS = "Select: complete the marquee selection"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.view.marquee.end(vpos)
        self.view._selectRect(self.view.marquee.rect(), modifiers & MouseModifier.CTRL)
        self.view.state.go(self.view.stateIdle)

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.view.marquee.resize(vpos)

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
        self.mouseLeftClick(vpos, spos, modifiers)


class DiagramViewStateEditPaste(ClickMixin, DiagramViewState):
    STATUS = "Paste: select the paste position"

    @checked
    def entry(
        self  : Self,
        items : Sequence[QGraphicsItem],
        spos  : QPointF | None = None
    ) -> None:
        spos = self._requireNoItemsSpos(items, spos)
        self.view.state.interact(EditPasteInteraction(
            self.view, self.view._snap(spos)
        ))


class DiagramViewStateEditDuplicate(ClickMixin, DragMixin, DiagramViewState):
    STATUS = "Duplicate: place the duplicated item(s) as required"


class DiagramViewStateEditSlide(ClickMixin, DragMixin, DiagramViewState):
    STATUS = "Slide: position the selected item(s) as required"
    SLIDE = True


class DiagramViewStateEditMove(DiagramViewStateEditSlide):
    STATUS = "Move: position the selected item(s) as required"
    SLIDE = False


class DiagramViewStateEditResize(ClickMixin, DragMixin, DiagramViewState):
    STATUS = "Resize: position the selected handle as required"


class DiagramViewStateEditMovePins(DiagramViewState):
    STATUS = "Move Pins: position the selected pin(s) as required"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        g = self.view.grid
        self._interaction().commit(spos, g.pitch if g.snap else None)
        self.view.state.go(self.view.stateIdle)

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        g = self.view.grid
        self._interaction().update(spos, g.pitch if g.snap else None)

    def mouseLeftDragCont(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        g = self.view.grid
        self._interaction().update(spos, g.pitch if g.snap else None)

    def mouseLeftDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        g = self.view.grid
        self._interaction().commit(spos, g.pitch if g.snap else None)
        self.view.state.go(self.view.stateIdle)


class DiagramViewStateEditAdjustPolySeg(DragMixin, DiagramViewState):
    STATUS = "Adjust Polyline Segment/Arc: position the selected grip as required"


class DiagramViewStateEditAppearance(DiagramViewState):
    STATUS = "Appearance: specify changes"

    @checked
    def entry(
        self  : Self,
        items : Sequence[QGraphicsItem],
        spos  : QPointF | None = None
    ) -> None:
        items = self._requireItemOrItemsElseNoSpos(
            items, self.view._selectedItems(), spos
        )
        dialog_items : list[ItemPresentationMixin] = [
            item for item in items
            if isinstance(item, ItemPresentationMixin)
        ]
        if dialog_items:
            dialog = AppearanceDialog(dialog_items, self.view)
            if dialog.exec():
                self.scene.editAppearance(
                    cast(list[QGraphicsItem], dialog_items),
                    dialog.getLineColorChoice(),
                    dialog.getLineWidthChoice(),
                    dialog.getLineStyleChoice(),
                    dialog.getFillColorChoice(),
                    dialog.getFillStyleChoice(),
                    dialog.getTextColorChoice(),
                    dialog.getTextFontChoice(),
                    dialog.getTextSizeChoice(),
                    dialog.getTextBoldChoice(),
                    dialog.getTextItalicChoice(),
                    dialog.getTextUnderlineChoice(),
                    undoable=True
                )
        else:
            logger().warning("No items selected")
        self.view.state.go(self.view.stateIdle)


class DiagramViewStateEditItemProperties(DiagramViewState):
    STATUS = "{Item} Properties: specify changes"

    @checked
    def entry(
        self  : Self,
        items : Sequence[QGraphicsItem],
        spos  : QPointF | None = None
    ) -> None:
        items = self._requireItemOrItemsElseNoSpos(
            items, self.view._selectedItems(), spos
        )
        dialog_items : list[PropertiesMixin] = [
            item for item in items
            if isinstance(item, PropertiesMixin)
        ]
        if len(dialog_items) == 1:
            dialog_item = dialog_items[0]
            dialog = PropertiesDialog(dialog_item, self.view)
            if dialog.exec():
                self.scene.editProperties(
                    dialog_item, dialog.getChanges(), undoable=True
                )
        else:
            logger().error(f"Expected 1 item, got {len(dialog_items)}")
        self.view.state.go(self.view.stateIdle)


class DiagramViewStateEditDiagramProperties(DiagramViewState):
    STATUS = "{Diagram} Properties: specify changes"

    @checked
    def entry(
        self  : Self,
        items : Sequence[QGraphicsItem],
        spos  : QPointF | None = None
    ) -> None:
        self._requireNoItemsNoSpos(items, spos)
        dialog = PropertiesDialog(self.scene, self.view)
        if dialog.exec():
            self.scene.editProperties(self.scene, dialog.getChanges(), undoable=True)
        self.view.state.go(self.view.stateIdle)

class DiagramViewStateEditQuery(DiagramViewState):
    STATUS = "Query: pick an item"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        self.view._selectClick(spos, modifiers)
        self.view.editQuery()


class DiagramViewStateEditText(DiagramViewState):
    STATUS = "Edit Text: specify changes"

    @checked
    def entry(
        self  : Self,
        items : Sequence[QGraphicsItem],
        spos  : QPointF | None = None
    ) -> None:
        items = self._requireItemOrItemsElseNoSpos(
            items, self.view._selectedItems(), spos
        )
        dialog_items = [item for item in items if isinstance(item, TextItem)]
        if len(dialog_items) == 1:
            dialog_item = dialog_items[0]
            dialog = TextItemDialog(dialog_item, self.view)
            if dialog.exec():
                self.scene.editText(
                    item       = dialog_item,
                    text       = dialog.getText(),
                    rotation   = dialog.getRotation(),
                    mirror_h   = dialog.getMirrorH(),
                    mirror_v   = dialog.getMirrorV(),
                    autoflip   = dialog.getAutoflip(),
                    origin     = dialog.getOrigin(),
                    align_h    = dialog.getAlignH(),
                    align_v    = dialog.getAlignV(),
                    pad_left   = dialog.getPadLeft(),
                    pad_right  = dialog.getPadRight(),
                    pad_top    = dialog.getPadTop(),
                    pad_bottom = dialog.getPadBottom(),
                    color      = dialog.getColor(),
                    font       = dialog.getFont(),
                    size       = dialog.getSize(),
                    bold       = dialog.getBold(),
                    italic     = dialog.getItalic(),
                    underline  = dialog.getUnderline(),
                    undoable   = True
                )
        else:
            logger().error(f"Expected 1 item, got {len(dialog_items)}")
        self.view.state.go(self.view.stateIdle)


class DiagramViewStateEditPropertyText(DiagramViewState):
    STATUS = "Edit Property Text: specify changes"

    @checked
    def entry(
        self  : Self,
        items : Sequence[QGraphicsItem],
        spos  : QPointF | None = None
    ) -> None:
        item = self._requireOneItemNoSpos(items, spos)
        if isinstance(item, PropertyTextItem):
            dialog = PropertyTextItemDialog(item, self.view)
            if dialog.exec():
                owner = item.owner()
                if not isinstance(owner, PropertiesMixin):
                    raise ValueError("Owner is not a PropertiesMixin")
                old_name = item.name()
                if old_name is None:
                    raise ValueError("Old name is None")
                new_name = dialog.getName()
                prop_name = old_name if isinstance(new_name, NoChange) \
                    else (old_name, new_name)
                text_name = old_name if isinstance(new_name, NoChange) \
                    else new_name
                self.scene.editProperty(
                    object   = owner,
                    name     = prop_name,
                    kind     = dialog.getKind(),
                    value    = dialog.getValue(),
                    undoable = True
                )
                self.scene.editPropertyText(
                    object    = owner,
                    name      = text_name,
                    cleat     = dialog.getCleat(),
                    rotation  = dialog.getRotation(),
                    mirror_h  = dialog.getMirrorH(),
                    mirror_v  = dialog.getMirrorV(),
                    autoflip  = dialog.getAutoflip(),
                    origin    = dialog.getOrigin(),
                    align_h   = dialog.getAlignH(),
                    align_v   = dialog.getAlignV(),
                    color     = dialog.getColor(),
                    font      = dialog.getFont(),
                    size      = dialog.getSize(),
                    bold      = dialog.getBold(),
                    italic    = dialog.getItalic(),
                    underline = dialog.getUnderline(),
                    undoable  = True
                )
        else:
            logger().warning("No property text selected")
        self.view.state.go(self.view.stateIdle)


class DiagramViewStateEditPort(DiagramViewState):
    STATUS = "Edit Port: specify changes"

    @checked
    def entry(
        self  : Self,
        items : Sequence[QGraphicsItem],
        spos  : QPointF | None = None
    ) -> None:
        item = self._requireOneItemNoSpos(items, spos)
        if isinstance(item, PortItem):
            dialog = PortPinItemDialog("Port", item, self.view)
            if dialog.exec():
                name = dialog.getName()
                direction = dialog.getDirection()
                self.scene.editPortPin(item, name, direction, undoable=True)
        else:
            logger().warning("No port selected")
        self.view.state.go(self.view.stateIdle)


class DiagramViewStateEditBlockPin(DiagramViewState):
    STATUS = "Edit Block Pin: specify changes"

    @checked
    def entry(
        self  : Self,
        items : Sequence[QGraphicsItem],
        spos  : QPointF | None = None
    ) -> None:
        item = self._requireOneItemNoSpos(items, spos)
        if isinstance(item, BlockPinItem):
            dialog = PortPinItemDialog("Block Pin", item, self.view)
            if dialog.exec():
                name = dialog.getName()
                direction = dialog.getDirection()
                self.scene.editPortPin(item, name, direction, undoable=True)
        else:
            logger().warning("No block pin selected")
        self.view.state.go(self.view.stateIdle)
