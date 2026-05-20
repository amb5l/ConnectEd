
from typing import Self
from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, \
                            QLabel, QLineEdit, QComboBox

from ....core.check import checked
from ....core.types import Direction

from ..components.layout.ok_cancel import OkCancelLayout

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...graphics.items.port_pin import PortPinMixin


class PortPinItemDialog(QDialog):
    _name_label       : QLabel
    _name_edit        : QLineEdit
    _signal_dir_label : QLabel
    _signal_dir_combo : QComboBox
    _name_dir_layout  : QHBoxLayout
    _ok_cancel_layout : OkCancelLayout
    _dialog_layout    : QVBoxLayout

    @checked
    def __init__(
        self   : Self,
        title  : str,
        item   : "PortPinMixin | None" = None,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self._dialog_layout = QVBoxLayout(self)
        self._name_dir_layout = QHBoxLayout()
        self._name_label = QLabel("Name:")
        self._name_dir_layout.addWidget(self._name_label)
        self._name_edit = QLineEdit()
        self._name_dir_layout.addWidget(self._name_edit)
        self._signal_dir_label = QLabel("Direction:")
        self._name_dir_layout.addWidget(self._signal_dir_label)
        self._signal_dir_combo = QComboBox()
        self._signal_dir_combo.addItems([e.value for e in Direction])
        self._name_dir_layout.addWidget(self._signal_dir_combo)
        self._dialog_layout.addLayout(self._name_dir_layout)
        self._ok_cancel_layout = OkCancelLayout(self)
        self._dialog_layout.addLayout(self._ok_cancel_layout)
        self.setLayout(self._dialog_layout)
        # default field values
        self._name_edit.setText("")
        self._signal_dir_combo.setCurrentIndex(0)
        # initialise fields from item if provided
        if item is not None:
            self._name_edit.setText(item.name())
            self._signal_dir_combo.setCurrentText(item.direction().value)

    @checked
    def getName(self : Self) -> str:
        return self._name_edit.text()

    @checked
    def getDirection(self : Self) -> Direction:
        return Direction(self._signal_dir_combo.currentText())
