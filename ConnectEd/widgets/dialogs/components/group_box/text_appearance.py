from typing import Self

from PyQt6.QtWidgets import QGroupBox, QWidget

from .....core.check import checked
from .....core.types import NoChange, Color, FontFamily, FontSize, FontBool

from ..layout.text_appearance import TextAppearancePreviewLayout


class TextAppearancePreviewGroupBox(QGroupBox):
    _layout : TextAppearancePreviewLayout


    def __init__(
        self              : Self,
        initial_color     : Color      | NoChange,
        initial_family    : FontFamily | NoChange,
        initial_size      : FontSize   | NoChange,
        initial_bold      : FontBool   | NoChange,
        initial_italic    : FontBool   | NoChange,
        initial_underline : FontBool   | NoChange,
        default_color     : Color      | NoChange,
        default_family    : FontFamily | NoChange,
        default_size      : FontSize   | NoChange,
        default_bold      : FontBool   | NoChange,
        default_italic    : FontBool   | NoChange,
        default_underline : FontBool   | NoChange,
        title             : str = "Appearance",
        parent            : QWidget | None = None
    ) -> None:
        super().__init__(title, parent)
        self._layout = TextAppearancePreviewLayout(
            initial_color,
            initial_family,
            initial_size,
            initial_bold,
            initial_italic,
            initial_underline,
            default_color,
            default_family,
            default_size,
            default_bold,
            default_italic,
            default_underline,
            parent
        )
        self.setLayout(self._layout)

    @checked
    def getColor(self : Self) -> Color | NoChange:
        return self._layout.getColor()

    @checked
    def getFamily(self : Self) -> FontFamily | NoChange:
        return self._layout.getFamily()

    @checked
    def getSize(self : Self) -> FontSize | NoChange:
        return self._layout.getSize()

    @checked
    def getBold(self : Self) -> FontBool | NoChange:
        return self._layout.getBold()

    @checked
    def getItalic(self : Self) -> FontBool | NoChange:
        return self._layout.getItalic()

    @checked
    def getUnderline(self : Self) -> FontBool | NoChange:
        return self._layout.getUnderline()
