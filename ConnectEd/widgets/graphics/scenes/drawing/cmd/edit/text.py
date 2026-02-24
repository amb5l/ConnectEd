from typing import Self

from PyQt6.QtGui import QColor

from .......core.check import checked
from .......core.types import Default, NoChange, NO_CHANGE, \
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
        text      : str              | NoChange = NO_CHANGE,
        block     : bool             | NoChange = NO_CHANGE,
        rot_angle : float            | NoChange = NO_CHANGE,
        rot_comp  : bool             | NoChange = NO_CHANGE,
        origin    : RectHandleId     | NoChange = NO_CHANGE,
        align_h   : AlignH           | NoChange = NO_CHANGE,
        align_v   : AlignV           | NoChange = NO_CHANGE,
        width     : float            | NoChange = NO_CHANGE,
        height    : float            | NoChange = NO_CHANGE,
        color     : QColor | Default | NoChange = NO_CHANGE,
        family    : str    | Default | NoChange = NO_CHANGE,
        size      : float  | Default | NoChange = NO_CHANGE,
        bold      : bool   | Default | NoChange = NO_CHANGE,
        italic    : bool   | Default | NoChange = NO_CHANGE,
        underline : bool   | Default | NoChange = NO_CHANGE
    ):
        super().__init__(scene, item)
        self._before = TextState.fromItem(item)
        change_args = {
            k: v for k, v in locals().items() \
                if k in TextChange.__dataclass_fields__.keys()
        }
        self._after = TextChange(**change_args)

    @checked
    def redo(self : Self) -> None:#
        if self._after.block is not NO_CHANGE:
            self._item.setBlock(self._after.block)
        if self._after.rot_angle is not NO_CHANGE:
            self._item.setRotation(self._after.rot_angle)
        if self._after.rot_comp is not NO_CHANGE:
            self._item.setRotComp(self._after.rot_comp)
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

    @checked
    def undo(self : Self) -> None:
        if self._after.text is not NO_CHANGE:
            self._item.setText(self._before.text)
        if self._after.block is not NO_CHANGE:
            self._item.setBlock(self._before.block)
        if self._after.rot_angle is not NO_CHANGE:
            self._item.setRotation(self._before.rot_angle)
        if self._after.rot_comp is not NO_CHANGE:
            self._item.setRotComp(self._before.rot_comp)
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
