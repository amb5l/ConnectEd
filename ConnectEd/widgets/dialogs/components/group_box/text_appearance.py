from typing import Self

from PyQt6.QtWidgets import QGroupBox, QWidget
from PyQt6.QtGui     import QColor

from .....core.check import checked
from .....core.types import NoChange

from ..layout.text_appearance import TextAppearancePreviewLayout


class TextAppearancePreviewGroupBox(QGroupBox):
    _layout : TextAppearancePreviewLayout

    @checked
    def __init__(
        self              : Self,
        initial_color     : QColor | None | NoChange,
        initial_family    : str    | None | NoChange,
        initial_size      : float  | None | NoChange,
        initial_bold      : bool   | None | NoChange,
        initial_italic    : bool   | None | NoChange,
        initial_underline : bool   | None | NoChange,
        default_color     : QColor,
        default_family    : str,
        default_size      : float,
        default_bold      : bool,
        default_italic    : bool,
        default_underline : bool,
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
    def getColor(self : Self) -> QColor | None | NoChange:
        return self._layout.getColor()

    @checked
    def getFamily(self : Self) -> str | None | NoChange:
        return self._layout.getFamily()

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
