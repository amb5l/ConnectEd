from typing import Self

from PyQt6.QtWidgets import QGroupBox, QWidget
from PyQt6.QtGui     import QColor

from .....core.check import checked
from .....core.types import NoChange

from ....graphics.presentation import TextTheme, TextOverrides

from ..layout.text_typography import TextTypographyPreviewLayout


class TextTypographyPreviewGroupBox(QGroupBox):
    _layout : TextTypographyPreviewLayout

    @checked
    def __init__(
        self     : Self,
        theme    : TextTheme,
        override : TextOverrides,
        title    : str = "Appearance",
        parent   : QWidget | None = None
    ) -> None:
        super().__init__(title, parent)
        self._layout = TextTypographyPreviewLayout(theme, override, parent)
        self.setLayout(self._layout)

    @checked
    def getColor(self : Self) -> QColor | None | NoChange:
        return self._layout.getColor()

    @checked
    def getFont(self : Self) -> str | None | NoChange:
        return self._layout.getFont()

    @checked
    def getSize(self : Self) -> float | None | NoChange:
        return self._layout.getSize()

    @checked
    def getBold(self : Self) -> bool | None | NoChange:
        return self._layout.getBold()

    @checked
    def getItalic(self : Self) -> bool | None | NoChange:
        return self._layout.getItalic()

    @checked
    def getUnderline(self : Self) -> bool | None | NoChange:
        return self._layout.getUnderline()
