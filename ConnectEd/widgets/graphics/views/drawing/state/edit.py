from typing import Self

from PyQt6.QtCore import QPoint, QPointF

from ......app import logger

from ......core.check import checked

from ......core.types import NO_CHANGE

from .....dialogs.properties          import PropertiesDialog
from .....dialogs.appearance          import AppearanceDialog
from .....dialogs.items.text          import TextItemDialog
from .....dialogs.items.property_text import PropertyTextItemDialog

from ....items.mixin         import ItemMixin
from ....items.text          import TextItem
from ....items.property_text import PropertyTextItem

from ..interaction.edit import EditPasteInteraction

from .base  import qkm, DrawingViewStateBase
from .mixin import ClickMixin, DragMixin


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


class DrawingViewStateEditPaste(ClickMixin, DrawingViewStateBase):
    STATUS = "Paste: select the paste position"

    @checked
    def entry(
        self : Self,
        v    : QPoint | None,
        s    : QPointF | None,
        i    : list[ItemMixin] | None = None
    ) -> None:
        self.view.state.interact(EditPasteInteraction(self.view, self._snap(s)))


class DrawingViewStateEditDuplicate(ClickMixin, DragMixin, DrawingViewStateBase):
    STATUS = "Duplicate: place the duplicated item(s) as required"


class DrawingViewStateEditSlide(ClickMixin, DragMixin, DrawingViewStateBase):
    STATUS = "Slide: position the selected item(s) as required"
    SLIDE = True


class DrawingViewStateEditMove(DrawingViewStateEditSlide):
    STATUS = "Move: position the selected item(s) as required"
    SLIDE = False


class DrawingViewStateEditResize(ClickMixin, DragMixin, DrawingViewStateBase):
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


class DrawingViewStateEditAdjustPolySeg(DragMixin, DrawingViewStateBase):
    STATUS = "Adjust Polyline Segment/Arc: position the selected grip as required"


class DrawingViewStateEditAppearance(DrawingViewStateBase):
    STATUS = "Appearance: specify changes"

    @checked
    def entry(
        self : Self,
        v    : QPoint | None,
        s    : QPointF | None,
        i    : list[ItemMixin] | None = None
    ) -> None:
        items = i or self.view._selectedItems(ItemMixin)
        if items:
            dialog = AppearanceDialog(items, self.view)
            if dialog.exec():
                self.scene.editAppearance(
                    items,
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


class DrawingViewStateEditItemProperties(DrawingViewStateBase):
    STATUS = "{Item} Properties: specify changes"

    @checked
    def entry(
        self : Self,
        v    : QPoint | None,
        s    : QPointF | None,
        i    : list[ItemMixin] | None = None
    ) -> None:
        item = i[0] if i else self.view._selectedItem(ItemMixin)
        if item:
            dialog = PropertiesDialog(item, self.view)
            if dialog.exec():
                self.scene.editProperties(item, dialog.getChanges(), undoable=True)
        else:
            logger().warning("No items selected")
        self.view.state.go(self.view.stateIdle)


class DrawingViewStateEditDrawingProperties(DrawingViewStateBase):
    STATUS = "{Drawing} Properties: specify changes"

    @checked
    def entry(
        self : Self,
        v    : QPoint | None,
        s    : QPointF | None,
        i    : list[ItemMixin] | None = None
    ) -> None:
        dialog = PropertiesDialog(self.scene, self.view)
        if dialog.exec():
            self.scene.editProperties(self.scene, dialog.getChanges(), undoable=True)
        self.view.state.go(self.view.stateIdle)

class DrawingViewStateEditQuery(DrawingViewStateBase):
    STATUS = "Query: pick an item"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view._selectPoint(s, m)
        self.view.editQuery()


class DrawingViewStateEditText(DrawingViewStateBase):
    STATUS = "Edit Text: specify changes"

    @checked
    def entry(
        self : Self,
        v    : QPoint | None,
        s    : QPointF | None,
        i    : list[ItemMixin] | None = None
    ) -> None:
        item = i[0] if i else self.view._selectedItem(TextItem)
        if item and isinstance(item, TextItem):
            dialog = TextItemDialog(item, self.view)
            if dialog.exec():
                self.scene.editText(
                    item      = item,
                    text      = dialog.getText(),
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
            logger().warning("No text selected")
        self.view.state.go(self.view.stateIdle)


class DrawingViewStateEditPropertyText(DrawingViewStateBase):
    STATUS = "Edit Property Text: specify changes"

    @checked
    def entry(
        self : Self,
        v    : QPoint | None,
        s    : QPointF | None,
        i    : list[ItemMixin] | None = None
    ) -> None:
        item = i[0] if i else self.view._selectedItem(PropertyTextItem)
        if item and isinstance(item, PropertyTextItem):
            dialog = PropertyTextItemDialog(item, self.view)
            if dialog.exec():
                old_name = item.name()
                new_name = dialog.getName()
                prop_name = old_name if new_name is NO_CHANGE else (old_name, new_name)
                text_name = old_name if new_name is NO_CHANGE else new_name
                self.scene.editProperty(
                    object   = item.owner(),
                    name     = prop_name,
                    kind     = dialog.getKind(),
                    value    = dialog.getValue(),
                    undoable = True
                )
                self.scene.editPropertyText(
                    object    = item.owner(),
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
