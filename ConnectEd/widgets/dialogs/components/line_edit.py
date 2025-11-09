from typing import Self

from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtGui     import QIntValidator, QDoubleValidator

class StringEdit(QLineEdit):
    def __init__(self : Self, value : str, parent=None):
        super().__init__(parent)
        self.setText(value)


class IntEdit(QLineEdit):
    def __init__(self : Self, value : int, parent=None):
        super().__init__(parent)
        self.setValidator(QIntValidator())
        self.setText(str(value))

    def setValue(self : Self, value : int) -> None:
        self.setText(str(value))

    def getValue(self : Self) -> int:
        try:
            return int(self.text())
        except ValueError:
            return 0


class FloatEdit(QLineEdit):
    def __init__(self : Self, value : float, parent=None):
        super().__init__(parent)
        self.setValidator(QDoubleValidator())
        self.setValue(value)

    def setValue(self : Self, value : float) -> None:
        self.setText(str(value))

    def getValue(self : Self) -> float:
        try:
            return float(self.text())
        except ValueError:
            return 0.0
