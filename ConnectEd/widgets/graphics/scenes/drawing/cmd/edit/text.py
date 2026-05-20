from typing import Self

from PyQt6.QtGui import QColor

from .......core.check import checked
from .......core.types import NoChange, NO_CHANGE, \
                              AlignH, AlignV, RectHandleId

from .....items.text import TextItem, TextState, TextChange

from .. import CmdSceneItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....scenes.drawing import DrawingScene


class CmdEditText(CmdSceneItem):
    _item   : "TextItem"
    _before : TextState
    _after  : TextChange

    @checked
    def __init__(
        self      : Self,
        scene     : "DrawingScene",
        item      : "TextItem",
        text      : str           | NoChange = NO_CHANGE,
        block     : bool          | NoChange = NO_CHANGE,
        rotation  : float         | NoChange = NO_CHANGE,
        mirror_h  : bool          | NoChange = NO_CHANGE,
        mirror_v  : bool          | NoChange = NO_CHANGE,
        autoflip  : bool          | NoChange = NO_CHANGE,
        origin    : RectHandleId  | NoChange = NO_CHANGE,
        align_h   : AlignH        | NoChange = NO_CHANGE,
        align_v   : AlignV        | NoChange = NO_CHANGE,
        width     : float         | NoChange = NO_CHANGE,
        height    : float         | NoChange = NO_CHANGE,
        color     : QColor | None | NoChange = NO_CHANGE,
        font      : str    | None | NoChange = NO_CHANGE,
        size      : float  | None | NoChange = NO_CHANGE,
        bold      : bool   | None | NoChange = NO_CHANGE,
        italic    : bool   | None | NoChange = NO_CHANGE,
        underline : bool   | None | NoChange = NO_CHANGE
    ):
        super().__init__(scene, item)
        self._before = TextState.fromItem(item)
        change_args = {
            k: v for k, v in locals().items() \
                if k in TextChange.__dataclass_fields__.keys()
        }
        self._after = TextChange(**change_args)

    @checked
    def redo(self : Self) -> None:
        if self._after.block is not NO_CHANGE:
            self._item.setBlock(self._after.block)
        if self._after.rotation is not NO_CHANGE:
            self._item.setRotation(self._after.rotation)
        if self._after.mirror_h is not NO_CHANGE:
            self._item.setMirrorH(self._after.mirror_h)
        if self._after.mirror_v is not NO_CHANGE:
            self._item.setMirrorV(self._after.mirror_v)
        if self._after.autoflip is not NO_CHANGE:
            self._item.setAutoflip(self._after.autoflip)
        if self._after.origin is not NO_CHANGE:
            # maintain scene position
            pos = self._item.getHandle(self._after.origin).scenePos()
            self._item.setOrigin(self._after.origin)
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
            self._item.setTextColor(self._after.color)
        if self._after.font is not NO_CHANGE:
            self._item.setTextFont(self._after.font)
        if self._after.size is not NO_CHANGE:
            self._item.setTextSize(self._after.size)
        if self._after.bold is not NO_CHANGE:
            self._item.setTextBold(self._after.bold)
        if self._after.italic is not NO_CHANGE:
            self._item.setTextItalic(self._after.italic)
        if self._after.underline is not NO_CHANGE:
            self._item.setTextUnderline(self._after.underline)

    @checked
    def undo(self : Self) -> None:
        if self._after.text is not NO_CHANGE:
            self._item.setText(self._before.text)
        if self._after.block is not NO_CHANGE:
            self._item.setBlock(self._before.block)
        if self._after.rotation is not NO_CHANGE:
            self._item.setRotation(self._before.rotation)
        if self._after.mirror_h is not NO_CHANGE:
            self._item.setMirrorH(self._before.mirror_h)
        if self._after.mirror_v is not NO_CHANGE:
            self._item.setMirrorV(self._before.mirror_v)
        if self._after.autoflip is not NO_CHANGE:
            self._item.setAutoflip(self._before.autoflip)
        if self._after.origin is not NO_CHANGE:
            # maintain scene position
            pos = self._item.getHandle(self._before.origin).scenePos()
            self._item.setOrigin(self._before.origin)
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
            self._item.setTextColor(self._before.color)
        if self._after.font is not NO_CHANGE:
            self._item.setTextFont(self._before.font)
        if self._after.size is not NO_CHANGE:
            self._item.setTextSize(self._before.size)
        if self._after.bold is not NO_CHANGE:
            self._item.setTextBold(self._before.bold)
        if self._after.italic is not NO_CHANGE:
            self._item.setTextItalic(self._before.italic)
        if self._after.underline is not NO_CHANGE:
            self._item.setTextUnderline(self._before.underline)
