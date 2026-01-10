from typing import Self

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QColor

from .....items import Default, NoChange, NO_CHANGE

from .....items.base_text import BaseTextBlock

from .text_line import CmdEditTextLine

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....drawing import DrawingScene


class CmdEditTextBlock(CmdEditTextLine):
    _item   : BaseTextBlock
    _before : CmdEditTextLine.ItemBefore
    _after  : CmdEditTextLine.ItemAfter

    def __init__(
        self      : Self,
        scene     : "DrawingScene",
        item      : BaseTextBlock,
        text      : str    | Default | NoChange = NO_CHANGE,
        color     : QColor | Default | NoChange = NO_CHANGE,
        font      : str    | Default | NoChange = NO_CHANGE,
        size      : float  | Default | NoChange = NO_CHANGE,
        bold      : bool   | Default | NoChange = NO_CHANGE,
        italic    : bool   | Default | NoChange = NO_CHANGE,
        underline : bool   | Default | NoChange = NO_CHANGE,
        alignment : Qt.AlignmentFlag | NoChange = NO_CHANGE,
        width     : float | None     | NoChange = NO_CHANGE,
        height    : float | None     | NoChange = NO_CHANGE,
        anchor    : str              | NoChange = NO_CHANGE
    ):
        super().__init__(
            scene, item, text, color, font, size, bold, italic, underline, anchor
        )
        self._before.alignment = item.alignment()
        self._before.width = item.width()
        self._before.height = item.height()
        self._after.alignment = alignment
        self._after.width = width
        self._after.height = height

    def redo(self : Self) -> None:
        if self._after.alignment is not NO_CHANGE:
            self._item.setAlignment(self._after.alignment)
        if self._after.width is not NO_CHANGE:
            self._item.setWidth(self._after.width)
        if self._after.height is not NO_CHANGE:
            self._item.setHeight(self._after.height)
        super().redo()

    def undo(self : Self) -> None:
        if self._before.alignment is not NO_CHANGE:
            self._item.setAlignment(self._before.alignment)
        if self._before.width is not NO_CHANGE:
            self._item.setWidth(self._before.width)
        if self._before.height is not NO_CHANGE:
            self._item.setHeight(self._before.height)
        super().undo()
