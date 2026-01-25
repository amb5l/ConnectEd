from typing      import Self
from dataclasses import dataclass

from PyQt6.QtGui import QColor

from .. import CmdSceneItem

from .....items import Default, NoChange, NO_CHANGE, AlignH, AlignV

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....scenes.drawing import DrawingScene
    from .....items.text     import TextItem


class CmdEditText(CmdSceneItem):
    _item : "TextItem"

    @dataclass
    class ItemBefore:
        text      : str
        block     : bool
        rotcomp   : bool
        origin    : str
        align_h   : AlignH
        align_v   : AlignV
        width     : float | None
        height    : float | None
        color     : QColor | Default
        family    : str    | Default
        size      : float  | Default
        bold      : bool   | Default
        italic    : bool   | Default
        underline : bool   | Default

    @dataclass
    class ItemAfter:
        text      : str              | NoChange = NO_CHANGE,
        block     : bool             | NoChange = NO_CHANGE,
        rotcomp   : bool             | NoChange = NO_CHANGE,
        origin    : str              | NoChange = NO_CHANGE,
        align_h   : AlignH           | NoChange = NO_CHANGE,
        align_v   : AlignV           | NoChange = NO_CHANGE,
        width     : float | None     | NoChange = NO_CHANGE,
        height    : float | None     | NoChange = NO_CHANGE,
        color     : QColor | Default | NoChange = NO_CHANGE,
        family    : str    | Default | NoChange = NO_CHANGE,
        size      : float  | Default | NoChange = NO_CHANGE,
        bold      : bool   | Default | NoChange = NO_CHANGE,
        italic    : bool   | Default | NoChange = NO_CHANGE,
        underline : bool   | Default | NoChange = NO_CHANGE,

    _item   : "TextItem"
    _before : ItemBefore
    _after  : ItemAfter

    def __init__(
        self      : Self,
        scene     : "DrawingScene",
        item      : "TextItem",
        text      : str    | Default | NoChange = NO_CHANGE,
        block     : bool             | NoChange = NO_CHANGE,
        rotcomp   : bool             | NoChange = NO_CHANGE,
        origin    : str              | NoChange = NO_CHANGE,
        align_h   : AlignH           | NoChange = NO_CHANGE,
        align_v   : AlignV           | NoChange = NO_CHANGE,
        width     : float | None     | NoChange = NO_CHANGE,
        height    : float | None     | NoChange = NO_CHANGE,
        color     : QColor | Default | NoChange = NO_CHANGE,
        family    : str    | Default | NoChange = NO_CHANGE,
        size      : float  | Default | NoChange = NO_CHANGE,
        bold      : bool   | Default | NoChange = NO_CHANGE,
        italic    : bool   | Default | NoChange = NO_CHANGE,
        underline : bool   | Default | NoChange = NO_CHANGE
    ):
        super().__init__(scene, item)
        self._before = self.ItemBefore(
            item.text(),
            item.block(),
            item.rotcomp(),
            item.getOrigin(),
            item.alignH(),
            item.alignV(),
            item.width(),
            item.height(),
            item.quillColor(),
            item.quillFamily(),
            item.quillSize(),
            item.quillBold(),
            item.quillItalic(),
            item.quillUnderline()
        )
        self._after = self.ItemAfter(
            text, block, rotcomp, origin, align_h, align_v, width, height, \
            color, family, size, bold, italic, underline
        )

    def redo(self : Self) -> None:#
        if self._after.block is not NO_CHANGE:
            self._item.setBlock(self._after.block)
        if self._after.rotcomp is not NO_CHANGE:
            self._item.setRotcomp(self._after.rotcomp)
        if self._after.origin is not NO_CHANGE:
            # maintain scene position
            pos = self._item.getHandle(self._after.anchor).scenePos()
            self._item.setOrigin(self._after.anchor)
            self._item.moveBy(pos - self._item.pos())
        if self._after.align_h is not NO_CHANGE:
            self._item.setAlignH(self._after.align_h)
        if self._after.align_v is not NO_CHANGE:
            self._item.setAlignV(self._after.align_v)
        if self._after.width is not NO_CHANGE:
            self._item.setWidth(self._after.width)
        if self._after.height is not NO_CHANGE:
            self._item.setHeight(self._after.height)
        if self._after.text is not NO_CHANGE:
            self._item.setText(self._after.text)
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
        if self._after.text is not NO_CHANGE:
            self._item.setText(self._before.text)
        if self._after.block is not NO_CHANGE:
            self._item.setBlock(self._before.block)
        if self._after.rotcomp is not NO_CHANGE:
            self._item.setRotcomp(self._before.rotcomp)
        if self._after.origin is not NO_CHANGE:
            # maintain scene position
            pos = self._item.getHandle(self._before.anchor).scenePos()
            self._item.setOrigin(self._before.anchor)
            self._item.moveBy(pos - self._item.pos())
        if self._after.align_h is not NO_CHANGE:
            self._item.setAlignH(self._before.align_h)
        if self._after.align_v is not NO_CHANGE:
            self._item.setAlignV(self._before.align_v)
        if self._after.width is not NO_CHANGE:
            self._item.setWidth(self._before.width)
        if self._after.height is not NO_CHANGE:
            self._item.setHeight(self._before.height)
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
        self._item.update()
