from typing import Self

from PyQt6.QtWidgets import QGroupBox, QWidget

from .....core.check import checked
from .....core.types import NoChange, AlignH, AlignV

from ..layout.text_align import TextAlignLayout


class TextAlignGroupBox(QGroupBox):
    _layout : TextAlignLayout

    def __init__(
        self    : Self,
        align_h : AlignH,
        align_v : AlignV,
        title   : str = "Alignment",
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(title, parent)
        self._layout = TextAlignLayout(align_h, align_v)
        self.setLayout(self._layout)

    @checked
    def getAlignH(self : Self) -> AlignH | NoChange:
        return self._layout.getAlignH()

    @checked
    def getAlignV(self : Self) -> AlignV | NoChange:
        return self._layout.getAlignV()
