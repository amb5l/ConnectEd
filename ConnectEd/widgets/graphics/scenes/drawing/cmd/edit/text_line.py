from typing      import Self
from dataclasses import dataclass

from PyQt6.QtGui import QColor

from .. import CmdSceneItem

from .....items import Default, NoChange, NO_CHANGE

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....scenes.drawing    import DrawingScene
    from .....items.base_text   import BaseTextLine


class CmdEditTextLine(CmdSceneItem):
    @dataclass
    class ItemBefore:
        text      : str
        color     : QColor | Default
        font      : str    | Default
        size      : float  | Default
        bold      : bool   | Default
        italic    : bool   | Default
        underline : bool   | Default
        anchor    : str

    @dataclass
    class ItemAfter:
        text      : str              | NoChange = NO_CHANGE,
        color     : QColor | Default | NoChange = NO_CHANGE,
        font      : str    | Default | NoChange = NO_CHANGE,
        size      : float  | Default | NoChange = NO_CHANGE,
        bold      : bool   | Default | NoChange = NO_CHANGE,
        italic    : bool   | Default | NoChange = NO_CHANGE,
        underline : bool   | Default | NoChange = NO_CHANGE,
        anchor    : str              | NoChange = NO_CHANGE

    _item   : "BaseTextLine"
    _before : ItemBefore
    _after  : ItemAfter

    def __init__(
        self      : Self,
        scene     : "DrawingScene",
        item      : "BaseTextLine",
        text      : str    | Default | NoChange = NO_CHANGE,
        color     : QColor | Default | NoChange = NO_CHANGE,
        font      : str    | Default | NoChange = NO_CHANGE,
        size      : float  | Default | NoChange = NO_CHANGE,
        bold      : bool   | Default | NoChange = NO_CHANGE,
        italic    : bool   | Default | NoChange = NO_CHANGE,
        underline : bool   | Default | NoChange = NO_CHANGE,
        anchor    : str              | NoChange = NO_CHANGE
    ):
        super().__init__(scene, item)
        self._before = self.ItemBefore(
            item.text(),
            item.quillColor(),
            item.quillFamily(),
            item.quillSize(),
            item.quillBold(),
            item.quillItalic(),
            item.quillUnderline(),
            item.getOrigin()
        )
        self._after = self.ItemAfter(
            text, color, font, size, bold, italic, underline, anchor
        )

    def redo(self : Self) -> None:
        if self._after.text is not NO_CHANGE:
            self._item.setText(self._after.text)
        if self._after.color is not NO_CHANGE:
            self._item.setQuillColor(self._after.color)
        if self._after.font is not NO_CHANGE:
            self._item.setQuillFamily(self._after.font)
        if self._after.size is not NO_CHANGE:
            self._item.setQuillSize(self._after.size)
        if self._after.bold is not NO_CHANGE:
            self._item.setQuillBold(self._after.bold)
        if self._after.italic is not NO_CHANGE:
            self._item.setQuillItalic(self._after.italic)
        if self._after.underline is not NO_CHANGE:
            self._item.setQuillUnderline(self._after.underline)
        if self._after.anchor is not NO_CHANGE:
            # maintain scene position
            pos = self._item.getHandle(self._after.anchor).scenePos()
            self._item.setOrigin(self._after.anchor)
            self._item.moveBy(pos - self._item.pos())
        self._item.update()

    def undo(self : Self) -> None:
        if self._after.text is not NO_CHANGE:
            self._item.setText(self._before.text)
        if self._after.color is not NO_CHANGE:
            self._item.setQuillColor(self._before.color)
        if self._after.font is not NO_CHANGE:
            self._item.setQuillFamily(self._before.font)
        if self._after.size is not NO_CHANGE:
            self._item.setQuillSize(self._before.size)
        if self._after.bold is not NO_CHANGE:
            self._item.setQuillBold(self._before.bold)
        if self._after.italic is not NO_CHANGE:
            self._item.setQuillItalic(self._before.italic)
        if self._after.underline is not NO_CHANGE:
            self._item.setQuillUnderline(self._before.underline)
        if self._after.anchor is not NO_CHANGE:
            # maintain scene position
            pos = self._item.getHandle(self._before.anchor).scenePos()
            self._item.setOrigin(self._before.anchor)
            self._item.moveBy(pos - self._item.pos())
        self._item.update()
