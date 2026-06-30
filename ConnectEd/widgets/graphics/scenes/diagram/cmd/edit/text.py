from __future__ import annotations

from typing import Self

from PyQt6.QtGui import QColor

from .......core.check import checked
from .......core.types import NoChange, NO_CHANGE, \
                              AlignH, AlignV, RectHandleId

from .....items.text import TextItem, TextState, TextChange

from .. import CmdSceneItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....scenes.diagram import DiagramScene


class CmdEditText(CmdSceneItem):
    _item   : TextItem
    _before : TextState
    _after  : TextChange

    @checked
    def __init__(
        self       : Self,
        scene      : DiagramScene,
        item       : TextItem,
        text       : str           | NoChange = NO_CHANGE,
        block      : bool          | NoChange = NO_CHANGE,
        rotation   : float         | NoChange = NO_CHANGE,
        mirror_h   : bool          | NoChange = NO_CHANGE,
        mirror_v   : bool          | NoChange = NO_CHANGE,
        autoflip   : bool          | NoChange = NO_CHANGE,
        origin     : RectHandleId  | NoChange = NO_CHANGE,
        align_h    : AlignH        | NoChange = NO_CHANGE,
        align_v    : AlignV        | NoChange = NO_CHANGE,
        width      : float         | NoChange = NO_CHANGE,
        height     : float         | NoChange = NO_CHANGE,
        pad_left   : float         | NoChange = NO_CHANGE,
        pad_right  : float         | NoChange = NO_CHANGE,
        pad_top    : float         | NoChange = NO_CHANGE,
        pad_bottom : float         | NoChange = NO_CHANGE,
        color      : QColor | None | NoChange = NO_CHANGE,
        font       : str    | None | NoChange = NO_CHANGE,
        size       : float  | None | NoChange = NO_CHANGE,
        bold       : bool   | None | NoChange = NO_CHANGE,
        italic     : bool   | None | NoChange = NO_CHANGE,
        underline  : bool   | None | NoChange = NO_CHANGE
    ) -> None:
        super().__init__(scene, item)
        self._before = TextState.fromItem(item)
        change_args = {
            k: v for k, v in locals().items() \
                if k in TextChange.__dataclass_fields__.keys()
        }
        self._after = TextChange(**change_args)

    @checked
    def redo(self : Self) -> None:
        if not isinstance(self._after.block, NoChange):
            self._item.setBlock(self._after.block)
        if not isinstance(self._after.rotation, NoChange):
            self._item.setRotation(self._after.rotation)
        if not isinstance(self._after.mirror_h, NoChange):
            self._item.setMirrorH(self._after.mirror_h)
        if not isinstance(self._after.mirror_v, NoChange):
            self._item.setMirrorV(self._after.mirror_v)
        if not isinstance(self._after.autoflip, NoChange):
            self._item.setAutoflip(self._after.autoflip)
        if not isinstance(self._after.origin, NoChange):
            self._item.setOrigin(self._after.origin)
        if not isinstance(self._after.align_h, NoChange):
            self._item.setAlignH(self._after.align_h)
        if not isinstance(self._after.align_v, NoChange):
            self._item.setAlignV(self._after.align_v)
        if not isinstance(self._after.width, NoChange):
            self._item.setWidth(self._after.width)
        if not isinstance(self._after.height, NoChange):
            self._item.setHeight(self._after.height)
        if not isinstance(self._after.pad_left, NoChange):
            self._item.setPadLeft(self._after.pad_left)
        if not isinstance(self._after.pad_right, NoChange):
            self._item.setPadRight(self._after.pad_right)
        if not isinstance(self._after.pad_top, NoChange):
            self._item.setPadTop(self._after.pad_top)
        if not isinstance(self._after.pad_bottom, NoChange):
            self._item.setPadBottom(self._after.pad_bottom)
        if not isinstance(self._after.text, NoChange):
            self._item.setText(self._after.text)
        if not isinstance(self._after.color, NoChange):
            self._item.setTextColor(self._after.color)
        if not isinstance(self._after.font, NoChange):
            self._item.setTextFont(self._after.font)
        if not isinstance(self._after.size, NoChange):
            self._item.setTextSize(self._after.size)
        if not isinstance(self._after.bold, NoChange):
            self._item.setTextBold(self._after.bold)
        if not isinstance(self._after.italic, NoChange):
            self._item.setTextItalic(self._after.italic)
        if not isinstance(self._after.underline, NoChange):
            self._item.setTextUnderline(self._after.underline)

    @checked
    def undo(self : Self) -> None:
        if not isinstance(self._after.text, NoChange):
            self._item.setText(self._before.text)
        if not isinstance(self._after.block, NoChange):
            self._item.setBlock(self._before.block)
        if not isinstance(self._after.rotation, NoChange):
            self._item.setRotation(self._before.rotation)
        if not isinstance(self._after.mirror_h, NoChange):
            self._item.setMirrorH(self._before.mirror_h)
        if not isinstance(self._after.mirror_v, NoChange):
            self._item.setMirrorV(self._before.mirror_v)
        if not isinstance(self._after.autoflip, NoChange):
            self._item.setAutoflip(self._before.autoflip)
        if not isinstance(self._after.origin, NoChange):
            self._item.setOrigin(self._before.origin)
        if not isinstance(self._after.align_h, NoChange):
            self._item.setAlignH(self._before.align_h)
        if not isinstance(self._after.align_v, NoChange):
            self._item.setAlignV(self._before.align_v)
        if not isinstance(self._after.width, NoChange):
            self._item.setWidth(self._before.width)
        if not isinstance(self._after.height, NoChange):
            self._item.setHeight(self._before.height)
        if not isinstance(self._after.pad_left, NoChange):
            self._item.setPadLeft(self._before.pad_left)
        if not isinstance(self._after.pad_right, NoChange):
            self._item.setPadRight(self._before.pad_right)
        if not isinstance(self._after.pad_top, NoChange):
            self._item.setPadTop(self._before.pad_top)
        if not isinstance(self._after.pad_bottom, NoChange):
            self._item.setPadBottom(self._before.pad_bottom)
        if not isinstance(self._after.color, NoChange):
            self._item.setTextColor(self._before.color)
        if not isinstance(self._after.font, NoChange):
            self._item.setTextFont(self._before.font)
        if not isinstance(self._after.size, NoChange):
            self._item.setTextSize(self._before.size)
        if not isinstance(self._after.bold, NoChange):
            self._item.setTextBold(self._before.bold)
        if not isinstance(self._after.italic, NoChange):
            self._item.setTextItalic(self._before.italic)
        if not isinstance(self._after.underline, NoChange):
            self._item.setTextUnderline(self._before.underline)
