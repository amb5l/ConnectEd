from typing import Self

from PyQt6.QtWidgets import QComboBox, QWidget

from .....core.check import checked
from .....core.types import NoChange, NO_CHANGE


class NetLabelNameComboBox(QComboBox):
    _ITEMS = ("Name", "Type")

    _initial : str

    @checked
    def __init__(
        self   : Self,
        name   : str,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setEditable(True)
        self.addItems(self._ITEMS)
        self._initial = name
        if name in self._ITEMS:
            self.setCurrentText(name)
        else:
            self.setEditText(name)

    @checked
    def value(self : Self) -> str | NoChange:
        r = self.currentText()
        return r if r != self._initial else NO_CHANGE
