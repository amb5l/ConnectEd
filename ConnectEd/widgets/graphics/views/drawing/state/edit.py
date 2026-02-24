from typing      import Self

from PyQt6.QtCore import QPoint, QPointF

from ......app import logger

from .....dialogs.properties     import PropertiesDialog
from .....dialogs.appearance     import AppearanceDialog
from .....dialogs.property_text  import PropertyTextDialog
from .....dialogs.items.port_pin import PortPinItemDialog
from .....dialogs.items.text     import TextItemDialog

from ....items               import ItemMixin
from ....items.text          import TextItem
from ....items.property_text import PropertyTextItem
from ....items.port          import PortItem
from ....items.block_pin     import BlockPinItem

from ....properties import PropertyAdd, PropertyEdit, PropertyDelete

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

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
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
                for edit in dialog.getEdits():
                    if isinstance(edit, PropertyAdd):
                        self.scene.addProperty(item, *edit.astuple(), undoable=True)
                    elif isinstance(edit, PropertyEdit):
                        self.scene.editProperty(item, *edit.astuple(), undoable=True)
                    elif isinstance(edit, PropertyDelete):
                        self.scene.delProperty(item, edit.name, undoable=True)
        else:
            logger().warning("No items selected")
        self.view.state.go(self.view.stateIdle)


class DrawingViewStateEditDrawingProperties(DrawingViewStateBase):
    STATUS = "{Drawing} Properties: specify changes"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        dialog = PropertiesDialog(self.scene, self.view)
        if dialog.exec():
            self.scene.editProperties(self.scene, dialog.getEdits(), undoable=True)
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
        item = i[0] if i else self.view._selectedItem(PortItem)
        if item:
            dialog = PortPinItemDialog("Port", item, self.view)
            if dialog.exec():
                name = dialog.getName()
                direction = dialog.getDirection()
                self.scene.editPortPin(item, name, direction, undoable=True)
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
        item = i[0] if i else self.view._selectedItem(BlockPinItem)
        if item and isinstance(item, BlockPinItem):
            dialog = PortPinItemDialog("Block Pin", item, self.view)
            if dialog.exec():
                name = dialog.getName()
                direction = dialog.getDirection()
                self.scene.editPortPin(item, name, direction, undoable=True)
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
        item = i[0] if i else self.view._selectedItem(TextItem)
        if item and isinstance(item, TextItem):
            dialog = TextItemDialog(item, self.view)
            if dialog.exec():
                self.scene.editText(
                    item      = item,
                    text      = dialog.getText(),
                    block     = dialog.getBlock(),
                    rot_angle = dialog.getRotAngle(),
                    rot_comp  = dialog.getRotComp(),
                    origin    = dialog.getOrigin(),
                    align_h   = dialog.getAlignH(),
                    align_v   = dialog.getAlignV(),
                    color     = dialog.getColor(),
                    family    = dialog.getFamily(),
                    size      = dialog.getSize(),
                    bold      = dialog.getBold(),
                    italic    = dialog.getItalic(),
                    underline = dialog.getUnderline(),
                    undoable  = True
                )
        else:
            logger().warning("No text block selected")
        self.view.state.go(self.view.stateIdle)


class DrawingViewStateEditPropertyText(DrawingViewStateBase):
    STATUS = "Edit Property Text: specify changes"

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        item = i[0] if i else self.view._selectedItem(PropertyTextItem)
        if item and isinstance(item, PropertyTextItem):
            dialog = PropertyTextDialog(item, self.view)
            if dialog.exec():
                value = dialog.getValue()
                appearance = dialog.getAppearanceChange()
                self.scene.editPropertyText(
                    item, value, appearance, undoable=True
                )
        else:
            logger().warning("No property text selected")
        self.view.state.go(self.view.stateIdle)
