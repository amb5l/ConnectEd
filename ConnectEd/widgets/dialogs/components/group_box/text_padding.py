from typing import Self

from PyQt6.QtWidgets import QGroupBox, QWidget

from .....core.check import checked
from .....core.types import NoChange

from ..layout.text_padding import TextPaddingLayout


class TextPaddingGroupBox(QGroupBox):
    _layout : TextPaddingLayout

    @checked
    def __init__(
        self         : Self,
        pad_top      : float,
        pad_bottom   : float,
        pad_left     : float,
        pad_right    : float,
        title        : str = "Padding",
        parent       : QWidget | None = None
    ) -> None:
        super().__init__(title, parent)
        self._layout = TextPaddingLayout(
            pad_top, pad_bottom, pad_left, pad_right
        )
        self.setLayout(self._layout)

    @checked
    def getPadLeft(self : Self) -> float | NoChange:
        return self._layout.getPadLeft()

    @checked
    def getPadRight(self : Self) -> float | NoChange:
        return self._layout.getPadRight()

    @checked
    def getPadTop(self : Self) -> float | NoChange:
        return self._layout.getPadTop()

    @checked
    def getPadBottom(self : Self) -> float | NoChange:
        return self._layout.getPadBottom()
