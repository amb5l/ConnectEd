from typing import Self

from PyQt6.QtWidgets import QGridLayout, QLabel, QHBoxLayout

from .....core.check import checked
from .....core.types import NoChange

from ..edit import StrEditor

from ..combo.net_label_name import NetLabelNameComboBox


class NetLabelItemLayout(QGridLayout):
    _name_label        : QLabel
    _name_value_layout : QHBoxLayout
    _name_value        : NetLabelNameComboBox
    _value_label       : QLabel
    _value_value       : StrEditor

    @checked
    def __init__(
        self  : Self,
        name  : str,
        value : str
    ) -> None:
        super().__init__()
        row = 0
        self._name_label = QLabel("Name:")
        self.addWidget(self._name_label, row, 0)
        self._name_value_layout = QHBoxLayout()
        self._name_value = NetLabelNameComboBox(name)
        self._name_value_layout.addWidget(self._name_value)
        self._name_value_layout.addStretch(1)
        self.addLayout(self._name_value_layout, row, 1)
        row += 1
        self._value_label = QLabel("Value:")
        self.addWidget(self._value_label, row, 0)
        self._value_value = StrEditor(value)
        self.addWidget(self._value_value, row, 1)

    @checked
    def getName(self : Self) -> str | NoChange:
        return self._name_value.value()

    @checked
    def getValue(self : Self) -> str | NoChange:
        return self._value_value.value()
