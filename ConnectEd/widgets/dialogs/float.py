from typing import Self

from PyQt6.QtWidgets import QWidget, QDialog, QLineEdit, \
                            QVBoxLayout, QHBoxLayout, QLabel

from ...core.check import checked

from .components.layout.ok_cancel import OkCancelLayout


class FloatDialog(QDialog):
    _dialog_layout    : QVBoxLayout
    _value_layout     : QHBoxLayout
    _value_label      : QLabel
    _value_input      : QLineEdit
    _ok_cancel_layout : OkCancelLayout

    @checked
    def __init__(
        self    : Self,
        initial : float | int | None = None,
        title   : str = "Value",
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self._dialog_layout = QVBoxLayout()
        # width section
        self._value_layout = QHBoxLayout()
        self._value_label = QLabel("Width:")
        self._value_layout.addWidget(self._value_label)
        self._value_input = QLineEdit("" if initial is None else str(initial))
        self._value_layout.addWidget(self._value_input)
        self._dialog_layout.addLayout(self._value_layout)
        # ok/cancel section
        self._ok_cancel_layout = OkCancelLayout(self)
        self._dialog_layout.addLayout(self._ok_cancel_layout)
        # set layout
        self.setLayout(self._dialog_layout)

    @checked
    def value(self : Self) -> float | None:
        try:
            return float(self._value_input.text())
        except ValueError:
            return None
