from typing import Self

from PyQt6.QtWidgets import QGroupBox, QWidget
from PyQt6.QtGui     import QColor

from .....core.check import checked
from .....core.types import Default, NoChange

from ..layout.text_appearance import TextAppearancePreviewLayout


class TextAppearancePreviewGroupBox(QGroupBox):
    _layout : TextAppearancePreviewLayout


    def __init__(
        self              : Self,
        initial_color     : QColor | Default | NoChange,
        initial_family    : str    | Default | NoChange,
        initial_size      : float  | Default | NoChange,
        initial_bold      : bool   | Default | NoChange,
        initial_italic    : bool   | Default | NoChange,
        initial_underline : bool   | Default | NoChange,
        default_color     : QColor | NoChange,
        default_family    : str    | NoChange,
        default_size      : float  | NoChange,
        default_bold      : bool   | NoChange,
        default_italic    : bool   | NoChange,
        default_underline : bool   | NoChange,
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
    def getColor(self : Self) -> QColor | Default | NoChange:
        return self._layout.getColor()

    @checked
    def getFamily(self : Self) -> str | Default | NoChange:
        return self._layout.getFamily()

    @checked
    def getSize(self : Self) -> float | Default | NoChange:
        return self._layout.getSize()

    @checked
    def getBold(self : Self) -> bool | Default | NoChange:
        return self._layout.getBold()

    @checked
    def getItalic(self : Self) -> bool | Default | NoChange:
        return self._layout.getItalic()

    @checked
    def getUnderline(self : Self) -> bool | Default | NoChange:
        return self._layout.getUnderline()
