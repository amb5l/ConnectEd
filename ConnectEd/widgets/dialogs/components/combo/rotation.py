from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox

from .....core.check import checked
from .....core.types import NoChange, NO_CHANGE

class RotationComboBox(QComboBox):
    _ANGLES = {
        "0"      : 0.0,
        "90 CW"  : 90.0,
        "180"    : 180.0,
        "90 CCW" : 270.0
    }

    _initial : float

    @checked
    def __init__(
        self   : Self,
        angle  : float,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        angle = angle % 360.0
        self._initial = angle
        for text, value in self._ANGLES.items():
            self.addItem(text, value)
            if angle == value:
                self.setCurrentIndex(self.count() - 1)

    @checked
    def value(self : Self) -> float | NoChange:
        r = self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)
        return r if r != self._initial else NO_CHANGE
