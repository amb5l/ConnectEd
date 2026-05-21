from typing import Self

from PyQt6.QtWidgets import QGridLayout, QLabel

from .....core.check import checked
from .....core.types import NoChange, NO_CHANGE

from ..edit import NaturalFloatEditor


class TextPaddingLayout(QGridLayout):
    _left_label    : QLabel
    _left_editor   : NaturalFloatEditor
    _right_label   : QLabel
    _right_editor  : NaturalFloatEditor
    _top_label     : QLabel
    _top_editor    : NaturalFloatEditor
    _bottom_label  : QLabel
    _bottom_editor : NaturalFloatEditor

    @checked
    def __init__(
        self        : Self,
        pad_top     : float,
        pad_bottom  : float,
        pad_left    : float,
        pad_right   : float
    ) -> None:
        super().__init__()
        # row 0 — horizontal padding
        self._left_label = QLabel("Left:")
        self.addWidget(self._left_label, 0, 0)
        self._left_editor = NaturalFloatEditor(pad_left)
        self.addWidget(self._left_editor, 0, 1)
        self._right_label = QLabel("Right:")
        self.addWidget(self._right_label, 0, 2)
        self._right_editor = NaturalFloatEditor(pad_right)
        self.addWidget(self._right_editor, 0, 3)
        # row 1 — vertical padding
        self._top_label = QLabel("Top:")
        self.addWidget(self._top_label, 1, 0)
        self._top_editor = NaturalFloatEditor(pad_top)
        self.addWidget(self._top_editor, 1, 1)
        self._bottom_label = QLabel("Bottom:")
        self.addWidget(self._bottom_label, 1, 2)
        self._bottom_editor = NaturalFloatEditor(pad_bottom)
        self.addWidget(self._bottom_editor, 1, 3)

    @checked
    def getPadLeft(self : Self) -> float | NoChange:
        r = self._left_editor.value()
        return NO_CHANGE if r is None else r

    @checked
    def getPadRight(self : Self) -> float | NoChange:
        r = self._right_editor.value()
        return NO_CHANGE if r is None else r

    @checked
    def getPadTop(self : Self) -> float | NoChange:
        r = self._top_editor.value()
        return NO_CHANGE if r is None else r

    @checked
    def getPadBottom(self : Self) -> float | NoChange:
        r = self._bottom_editor.value()
        return NO_CHANGE if r is None else r
