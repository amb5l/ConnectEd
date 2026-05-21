from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QLineEdit, QTextEdit, QCheckBox, QWidget
from PyQt6.QtGui     import QFontMetrics, QIntValidator, QDoubleValidator, QValidator

from ....core.check import checked

from ....core.types import NoChange, NO_CHANGE


class SizeValidator(QValidator):
    @checked
    def validate(
        self : Self, text : str, pos : int
    ) -> tuple[QValidator.State, str, int]:
        text = text.strip()
        if text == "":
            return QValidator.State.Acceptable, text, pos
        try:
            val = float(text)
        except ValueError:
            return QValidator.State.Invalid, text, pos
        if val < 0:
            return QValidator.State.Acceptable, "", 0
        return QValidator.State.Acceptable, text, pos


class NaturalFloatValidator(QDoubleValidator):
    @checked
    def __init__(self : Self, parent : QWidget | None = None) -> None:
        super().__init__(parent)
        self.setBottom(0.0)


class StrEditor(QLineEdit):
    _initial : str | None

    @checked
    def __init__(
        self   : Self,
        value  : str | None = None,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._initial = value
        self.setText("" if value is None else value)

    @checked
    def value(self : Self) -> str | NoChange:
        return NO_CHANGE if self.text() == self._initial else self.text()

    @checked
    def setValue(self : Self, value : str) -> None:
        self.setText(value)


class TextEditor(QTextEdit):
    _initial : str | None

    @checked
    def __init__(
        self   : Self,
        value  : str | None = None,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._initial = value
        self.setPlainText("" if value is None else value)

    @checked
    def text(self : Self) -> str:
        return self.toPlainText()

    @checked
    def value(self : Self) -> str | NoChange:
        return NO_CHANGE if self.toPlainText() == self._initial else self.toPlainText()

    @checked
    def setValue(self : Self, value : str) -> None:
        self.setPlainText(value)


class IntEditor(QLineEdit):
    _initial : int | None

    @checked
    def __init__(
        self   : Self,
        value  : int | None = None,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._initial = value
        self.setValidator(QIntValidator())
        self.setText("" if value is None else str(value))

    @checked
    def value(self : Self) -> int | NoChange | None:
        try:
            r = int(self.text())
        except ValueError:
            r = None
        return r if r != self._initial else NO_CHANGE

    @checked
    def setValue(self : Self, value : int) -> None:
        self.setText(str(value))


class FloatEditor(QLineEdit):
    _initial : float | None

    @checked
    def __init__(
        self   : Self,
        value  : float | None = None,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._initial = value
        self.setValidator(QDoubleValidator())
        self.setText("" if value is None else str(value))

    @checked
    def value(self : Self) -> float | NoChange | None:
        try:
            r = float(self.text())
        except ValueError:
            r = None
        return r if r != self._initial else NO_CHANGE

    @checked
    def setValue(self : Self, value : float) -> None:
        self.setText(str(value))


class NaturalFloatEditor(QLineEdit):
    _initial : float

    @checked
    def __init__(
        self   : Self,
        value  : float         = 0.0,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._initial = value
        self.setValidator(NaturalFloatValidator())
        self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.setText(str(value))
        metrics = QFontMetrics(self.font())
        self.setFixedWidth(metrics.horizontalAdvance("999.9") + 8)

    @checked
    def value(self : Self) -> float | NoChange | None:
        try:
            r = float(self.text())
        except ValueError:
            r = None
        return r if r != self._initial else NO_CHANGE

    @checked
    def setValue(self : Self, value : float) -> None:
        self.setText(str(value))


class SizeEditor(QLineEdit):
    _initial : float | None

    @checked
    def __init__(
        self   : Self,
        value  : float | None = None,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._initial = value
        self.setValidator(SizeValidator())
        self.setText("" if value is None else str(value))

    @checked
    def value(self : Self) -> float | NoChange:
        try:
            r = float(self.text())
        except ValueError:
            r = -1.0  # auto size
        return r if r != self._initial else NO_CHANGE

    @checked
    def setValue(self : Self, value : float) -> None:
        self.setText(str(value))


class BoolEditor(QCheckBox):
    _initial : bool | None

    @checked
    def __init__(
        self   : Self,
        value  : bool | None = None,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._initial = value
        self.setChecked(value is True)

    @checked
    def value(self : Self) -> bool | NoChange:
        r = self.isChecked()
        return r if r != self._initial else NO_CHANGE

    @checked
    def setValue(self : Self, value : bool) -> None:
        self.setChecked(value is True)
