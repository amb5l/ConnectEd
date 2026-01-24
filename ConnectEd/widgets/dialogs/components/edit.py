from typing import Self

from PyQt6.QtWidgets import QLineEdit, QTextEdit, QHBoxLayout, QToolButton
from PyQt6.QtGui     import QIntValidator, QDoubleValidator


class TextLineEditor(QLineEdit):
    def __init__(self : Self, value : str, parent=None):
        super().__init__(parent)
        self.setText(value)


class IntEditor(QLineEdit):
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


class FloatEditor(QLineEdit):
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


class TextBlockEditor(QTextEdit):
    def __init__(self : Self, value : str, parent=None):
        super().__init__(parent)
        self.setPlainText(value)

    def text(self : Self) -> str:
        return self.toPlainText()


class TextEditor(QHBoxLayout):
    _editor : TextLineEditor
    _button : QToolButton

    def __init__(self : Self, value : str, parent=None):
        super().__init__(parent)
        self._editor = TextLineEditor(value, parent)
        self._button = QToolButton(parent)
        self._button.setText("...")
        self._button.clicked.connect(self._onButtonClick)
        self.addWidget(self._editor)
        self.addWidget(self._button)

    def getText(self : Self) -> str:
        return self._editor.text()

    def _onButtonClick(self : Self) -> None:
        # launch text editor dialog
        pass
