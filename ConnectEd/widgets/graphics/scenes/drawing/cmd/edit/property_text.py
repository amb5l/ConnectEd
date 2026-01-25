from typing      import Self
from dataclasses import dataclass

from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QColor

from .. import CmdSceneItem

from .....items import Default, NoChange, NO_CHANGE

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....scenes.drawing      import DrawingScene
    from .....items.property_text import PropertyTextMixin
    from .....items.mixin.quill   import ItemQuillMixin


class CmdEditPropertyText(CmdSceneItem):
    @dataclass
    class ItemBefore:
        value     : str
        color     : QColor | Default
        family    : str    | Default
        size      : float  | Default
        bold      : bool   | Default
        italic    : bool   | Default
        underline : bool   | Default

    @dataclass
    class ItemAfter:
        value     : str
        color     : QColor | Default | NoChange
        family    : str    | Default | NoChange
        size      : float  | Default | NoChange
        bold      : bool   | Default | NoChange
        italic    : bool   | Default | NoChange
        underline : bool   | Default | NoChange

    _item   : "QGraphicsItem | PropertyTextMixin | ItemQuillMixin"
    _before : ItemBefore
    _after  : ItemAfter

    def __init__(
        self      : Self,
        scene     : "DrawingScene",
        item      : "PropertyTextMixin | ItemQuillMixin",
        value     : str              | NoChange = NO_CHANGE,
        color     : QColor | Default | NoChange = NO_CHANGE,
        family    : str    | Default | NoChange = NO_CHANGE,
        size      : float  | Default | NoChange = NO_CHANGE,
        bold      : bool   | Default | NoChange = NO_CHANGE,
        italic    : bool   | Default | NoChange = NO_CHANGE,
        underline : bool   | Default | NoChange = NO_CHANGE,
    ):
        super().__init__(scene, item)
        self._item           = item
        self._before = self.ItemBefore(
            item.value(),
            item.quillColor(),
            item.quillFamily(),
            item.quillSize(),
            item.quillBold(),
            item.quillItalic(),
            item.quillUnderline()
        )
        self._after = self.ItemAfter(
            value, color, family, size, bold, italic, underline
        )

    def redo(self : Self) -> None:
        if self._after.value is not NO_CHANGE:
            self._item.setValue(self._after.value)
        if self._after.color is not NO_CHANGE:
            self._item.setQuillColor(self._after.color)
        if self._after.family is not NO_CHANGE:
            self._item.setQuillFamily(self._after.family)
        if self._after.size is not NO_CHANGE:
            self._item.setQuillSize(self._after.size)
        if self._after.bold is not NO_CHANGE:
            self._item.setQuillBold(self._after.bold)
        if self._after.italic is not NO_CHANGE:
            self._item.setQuillItalic(self._after.italic)
        if self._after.underline is not NO_CHANGE:
            self._item.setQuillUnderline(self._after.underline)
        self._item.update()

    def undo(self : Self) -> None:
        if self._after.value is not NO_CHANGE:
            self._item.setValue(self._before.value)
        if self._after.color is not NO_CHANGE:
            self._item.setQuillColor(self._before.color)
        if self._after.family is not NO_CHANGE:
            self._item.setQuillFamily(self._before.family)
        if self._after.size is not NO_CHANGE:
            self._item.setQuillSize(self._before.size)
        if self._after.bold is not NO_CHANGE:
            self._item.setQuillBold(self._before.bold)
        if self._after.italic is not NO_CHANGE:
            self._item.setQuillItalic(self._before.italic)
        if self._after.underline is not NO_CHANGE:
            self._item.setQuillUnderline(self._before.underline)
