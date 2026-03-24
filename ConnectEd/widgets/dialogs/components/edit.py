from typing import Self

from PyQt6.QtWidgets import QLineEdit, QTextEdit, QCheckBox, QWidget
from PyQt6.QtGui     import QIntValidator, QDoubleValidator, QValidator


class UniqueStrValidator(QValidator):
    """Accepts text not present in an exclusion list."""

    _exclude : list[str]

    def __init__(
        self    : Self,
        exclude : list[str],
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._exclude = exclude

    def validate(
        self : Self, text : str, pos : int
    ) -> tuple[QValidator.State, str, int]:
        if text in self._exclude:
            state = QValidator.State.Intermediate
        else:
            state = QValidator.State.Acceptable
        return state, text, pos


class NameStrValidator(UniqueStrValidator):
    def validate(
        self : Self, text : str, pos : int
    ) -> tuple[QValidator.State, str, int]:
        state, text, pos = super().validate(text, pos)
        if text == "":
            state = QValidator.State.Intermediate
        return state, text, pos


class StrEditor(QLineEdit):
    def __init__(
        self    : Self,
        value   : str | None = None,
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setText("" if value is None else value)

    def value(self : Self) -> str:
        return self.text()

    def setValue(self : Self, value : str) -> None:
        self.setText(value)


class NameStrEditor(StrEditor):
    _STYLE_INVALID = "QLineEdit { border: 1px solid red; }"

    def __init__(
        self    : Self,
        value   : str | None = None,
        exclude : list[str] | None = None,
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(value, parent)
        self.setValidator(NameStrValidator(exclude or [], self))
        self.textChanged.connect(self._updateStyle)
        self._updateStyle(self.text())

    def _updateStyle(self : Self, _text : str) -> None:
        self.setStyleSheet("" if self.hasAcceptableInput() else self._STYLE_INVALID)


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
        self.setChecked(False if value is None else value)

    def value(self : Self) -> bool:
        return self.isChecked()

    def setValue(self : Self, value : bool | None) -> None:
        self.setChecked(False if value is None else value)
