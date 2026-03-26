from typing import Self

from PyQt6.QtWidgets import QComboBox, QWidget

from .....core.check import checked
from .....core.types import NoChange, NO_CHANGE


class TextFormatComboBox(QComboBox):
    _initial : bool

    @checked
    def __init__(self : Self, block : bool, parent : QWidget | None = None) -> None:
        self._initial = block
        super().__init__(parent)
        self.addItem("Line", False)
        self.addItem("Block", True)
        self.setCurrentIndex(1 if block else 0)

    @checked
    def raw(self : Self) -> bool:
        return self.currentIndex() == 1

    @checked
    def value(self : Self) -> bool | NoChange:
        r = self.raw()
        return r if r != self._initial else NO_CHANGE
