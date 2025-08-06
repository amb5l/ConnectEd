from typing import Self

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, \
                            QGroupBox, QLabel, QLineEdit, QComboBox, \
                            QCheckBox, QRadioButton, QPushButton

from ..drawing.items import SignalDirection, RangeDirection, VectorRange

from . import okCancelLayout


class PlacePortPinDialog(QDialog):
    name_label       : QLabel
    name_edit        : QLineEdit
    signal_dir_label : QLabel
    signal_dir_combo : QComboBox
    name_dir_layout  : QHBoxLayout
    scalar_check     : QCheckBox
    left_label       : QLabel
    left_edit        : QLineEdit
    right_label      : QLabel
    right_edit       : QLineEdit
    range_lr_layout  : QGridLayout
    unspec_radio     : QRadioButton
    down_radio       : QRadioButton
    up_radio         : QRadioButton
    range_dir_layout : QHBoxLayout
    range_dir_group  : QGroupBox
    range_layout     : QHBoxLayout
    range_group      : QGroupBox
    width_layout     : QHBoxLayout
    ok_button        : QPushButton
    cancel_button    : QPushButton
    ok_cancel_layout : QHBoxLayout
    dialog_layout    : QVBoxLayout

    def __init__(self : Self, title : str):
        super().__init__()
        self.setWindowTitle(title)
        self.dialog_layout = QVBoxLayout(self)
        self.name_dir_layout = QHBoxLayout()
        self.name_label = QLabel("Name:")
        self.name_dir_layout.addWidget(self.name_label)
        self.name_edit = QLineEdit()
        self.name_dir_layout.addWidget(self.name_edit)
        self.signal_dir_label = QLabel("Direction:")
        self.name_dir_layout.addWidget(self.signal_dir_label)
        self.signal_dir_combo = QComboBox()
        self.signal_dir_combo.addItems([e.value for e in SignalDirection])
        self.name_dir_layout.addWidget(self.signal_dir_combo)
        self.dialog_layout.addLayout(self.name_dir_layout)
        self.width_layout = QHBoxLayout()
        self.scalar_check = QCheckBox("Scalar")
        self.scalar_check.setChecked(True)
        self.width_layout.addWidget(self.scalar_check)
        self.range_group = QGroupBox("Vector Range:")
        self.range_layout = QVBoxLayout()
        self.range_lr_layout = QGridLayout()
        self.left_label = QLabel("Left:")
        self.range_lr_layout.addWidget(self.left_label, 0, 0)
        self.left_edit = QLineEdit()
        self.range_lr_layout.addWidget(self.left_edit, 1, 0)
        self.colon_label = QLabel(":")
        self.range_lr_layout.addWidget(self.colon_label, 1, 1)
        self.right_label = QLabel("Right:")
        self.range_lr_layout.addWidget(self.right_label, 0, 2)
        self.right_edit = QLineEdit()
        self.range_lr_layout.addWidget(self.right_edit, 1, 2)
        self.range_layout.addLayout(self.range_lr_layout)
        self.range_dir_group = QGroupBox("Direction:")
        self.range_dir_layout = QHBoxLayout()
        self.unspec_radio = QRadioButton("Unspecified")
        self.unspec_radio.setChecked(True)
        self.range_dir_layout.addWidget(self.unspec_radio)
        self.down_radio = QRadioButton("Down")
        self.range_dir_layout.addWidget(self.down_radio)
        self.up_radio = QRadioButton("Up")
        self.range_dir_layout.addWidget(self.up_radio)
        self.range_dir_group.setLayout(self.range_dir_layout)
        self.range_layout.addWidget(self.range_dir_group)
        self.range_group.setLayout(self.range_layout)
        self.range_group.setEnabled(False)
        self.width_layout.addWidget(self.range_group)
        self.dialog_layout.addLayout(self.width_layout)
        okCancelLayout(self)
        self.setLayout(self.dialog_layout)
        self.scalar_check.stateChanged.connect(self.onScalarChanged)

    def onScalarChanged(self, state: int) -> None:
        self.range_group.setEnabled(state == 0)

    def getName(self : Self) -> str:
        return self.name_edit.text()

    def getDirection(self : Self) -> SignalDirection:
        return SignalDirection(self.signal_dir_combo.currentText())

    def getRange(self : Self) -> VectorRange | None:
        if self.scalar_check.isChecked():
            return None
        range_dir = \
            RangeDirection.UP if self.up_radio.isChecked() \
            else RangeDirection.DOWN if self.down_radio.isChecked() \
            else RangeDirection.UNSPECIFIED
        return VectorRange(
            int(self.left_edit.text()),
            range_dir,
            int(self.right_edit.text())
        )
