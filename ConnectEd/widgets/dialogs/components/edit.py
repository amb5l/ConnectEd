from typing import Self

from PyQt6.QtWidgets import QLineEdit, QTextEdit, QCheckBox, QWidget
from PyQt6.QtGui     import QIntValidator, QDoubleValidator


class StrEditor(QLineEdit):
    def __init__(self : Self, value : str | None = None, parent : QWidget | None = None):
        super().__init__(parent)
        self.setText("" if value is None else value)

    def value(self : Self) -> str:
        return self.text()

    def setValue(self : Self, value : str) -> None:
        self.setText(value)


class TextEditor(QTextEdit):
    def __init__(self : Self, value : str | None = None, parent : QWidget | None = None):
        super().__init__(parent)
        self.setPlainText("" if value is None else value)

    def value(self : Self) -> str:
        return self.toPlainText()

    def setValue(self : Self, value : str) -> None:
        self.setPlainText(value)


class IntEditor(QLineEdit):
    def __init__(self : Self, value : int | None = None, parent : QWidget | None = None):
        super().__init__(parent)
        self.setValidator(QIntValidator())
        self.setText("" if value is None else str(value))

    def value(self : Self) -> int:
        try:
            return int(self.text())
        except ValueError:
            return 0

    def setValue(self : Self, value : int) -> None:
        self.setText(str(value))


class FloatEditor(QLineEdit):
    def __init__(self : Self, value : float | None = None, parent : QWidget | None = None):
        super().__init__(parent)
        self.setValidator(QDoubleValidator())
        self.setText("" if value is None else str(value))

    def value(self : Self) -> float:
        try:
            return float(self.text())
        except ValueError:
            return 0.0

    def setValue(self : Self, value : float) -> None:
        self.setText(str(value))


class BoolEditor(QCheckBox):
    def __init__(self : Self, value : bool | None = None, parent : QWidget | None = None):
        super().__init__(parent)
        self.setChecked("" if value is None else value)

    def value(self : Self) -> bool:
        return self.isChecked()

    def setValue(self : Self, value : bool) -> None:
        self.setChecked(value)
