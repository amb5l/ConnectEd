from typing import Self

from PyQt6.QtWidgets import QWidget, QDialog, \
                            QVBoxLayout, QHBoxLayout, QGridLayout, \
                            QGroupBox, QLabel, QLineEdit, QComboBox, \
                            QCheckBox, QRadioButton, QPushButton

from ..graphics.items import SignalDirection, RangeDirection, VectorRange

from . import okCancelLayout

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..graphics.items.port_pin import PortPinMixin


class PortPinDialog(QDialog):
    _name_label       : QLabel
    _name_edit        : QLineEdit
    _signal_dir_label : QLabel
    _signal_dir_combo : QComboBox
    _name_dir_layout  : QHBoxLayout
    _scalar_check     : QCheckBox
    _left_label       : QLabel
    _left_edit        : QLineEdit
    _right_label      : QLabel
    _right_edit       : QLineEdit
    _range_lr_layout  : QGridLayout
    _unspec_radio     : QRadioButton
    _down_radio       : QRadioButton
    _up_radio         : QRadioButton
    _range_dir_layout : QHBoxLayout
    _range_dir_group  : QGroupBox
    _range_layout     : QHBoxLayout
    _range_group      : QGroupBox
    _width_layout     : QHBoxLayout
    _ok_button        : QPushButton
    _cancel_button    : QPushButton
    _ok_cancel_layout : QHBoxLayout
    _dialog_layout    : QVBoxLayout

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
        self._signal_dir_combo.addItems([e.value for e in SignalDirection])
        self._name_dir_layout.addWidget(self._signal_dir_combo)
        self._dialog_layout.addLayout(self._name_dir_layout)
        self._width_layout = QHBoxLayout()
        self._scalar_check = QCheckBox("Scalar")
        self._scalar_check.setChecked(True)
        self._width_layout.addWidget(self._scalar_check)
        self._range_group = QGroupBox("Vector Range:")
        self._range_layout = QVBoxLayout()
        self._range_lr_layout = QGridLayout()
        self._left_label = QLabel("Left:")
        self._range_lr_layout.addWidget(self._left_label, 0, 0)
        self._left_edit = QLineEdit()
        self._range_lr_layout.addWidget(self._left_edit, 1, 0)
        self.colon_label = QLabel(":")
        self._range_lr_layout.addWidget(self.colon_label, 1, 1)
        self._right_label = QLabel("Right:")
        self._range_lr_layout.addWidget(self._right_label, 0, 2)
        self._right_edit = QLineEdit()
        self._range_lr_layout.addWidget(self._right_edit, 1, 2)
        self._range_layout.addLayout(self._range_lr_layout)
        self._range_dir_group = QGroupBox("Direction:")
        self._range_dir_layout = QHBoxLayout()
        self._unspec_radio = QRadioButton("Unspecified")
        self._unspec_radio.setChecked(True)
        self._range_dir_layout.addWidget(self._unspec_radio)
        self._down_radio = QRadioButton("Down")
        self._range_dir_layout.addWidget(self._down_radio)
        self._up_radio = QRadioButton("Up")
        self._range_dir_layout.addWidget(self._up_radio)
        self._range_dir_group.setLayout(self._range_dir_layout)
        self._range_layout.addWidget(self._range_dir_group)
        self._range_group.setLayout(self._range_layout)
        self._range_group.setEnabled(False)
        self._width_layout.addWidget(self._range_group)
        self._dialog_layout.addLayout(self._width_layout)
        okCancelLayout(self)
        self.setLayout(self._dialog_layout)
        # default field values
        self._name_edit.setText("")
        self._signal_dir_combo.setCurrentIndex(0)
        self._scalar_check.setChecked(True)
        self._range_group.setEnabled(False)
        self._left_edit.setText("")
        self._right_edit.setText("")
        self._unspec_radio.setChecked(True)
        self._down_radio.setChecked(False)
        self._up_radio.setChecked(False)
        # initialise fields from item if provided
        if item is not None:
            self._name_edit.setText(item.name)
            self._signal_dir_combo.setCurrentText(item.direction.value)
            if item.range is None:
                self._scalar_check.setChecked(True)
                self._range_group.setEnabled(False)
            else:
                self._scalar_check.setChecked(False)
                self._range_group.setEnabled(True)
                self._left_edit.setText(str(item.range.left))
                self._right_edit.setText(str(item.range.right))
                self._up_radio.setChecked(
                    item.range.dir == RangeDirection.UP
                )
                self._down_radio.setChecked(
                    item.range.dir == RangeDirection.DOWN
                )
                self._unspec_radio.setChecked(
                    item.range.dir == RangeDirection.UNSPECIFIED
                )
        # catch scalar/vector change
        self._scalar_check.stateChanged.connect(self.onScalarChanged)

    def onScalarChanged(self : Self, state : int) -> None:
        self._range_group.setEnabled(state == 0)

    def getName(self : Self) -> str:
        return self._name_edit.text()

    def getDirection(self : Self) -> SignalDirection:
        return SignalDirection(self._signal_dir_combo.currentText())

    def getRange(self : Self) -> VectorRange | None:
        if self._scalar_check.isChecked():
            return None
        range_dir = \
            RangeDirection.UP if self._up_radio.isChecked() \
            else RangeDirection.DOWN if self._down_radio.isChecked() \
            else RangeDirection.UNSPECIFIED
        return VectorRange(
            int(self._left_edit.text()),
            range_dir,
            int(self._right_edit.text())
        )
