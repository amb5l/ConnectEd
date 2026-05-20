from typing import Self

from PyQt6.QtWidgets import QWidget, QDialog, \
                            QVBoxLayout, QHBoxLayout, QGroupBox, \
                            QLabel, QComboBox, QRadioButton

from ...core.check import checked

from .components.layout.ok_cancel import OkCancelLayout


ANGLE_PRESETS = [30, 45, 60, 90, 180]


class ArcDialog(QDialog):
    # instance attributes
    _dialog_layout    : QVBoxLayout
    _angle_layout     : QHBoxLayout
    _angle_label      : QLabel
    _angle_combo      : QComboBox
    _degrees_label    : QLabel
    _direction_group  : QGroupBox
    _direction_layout : QHBoxLayout
    _cw_radio         : QRadioButton
    _ccw_radio        : QRadioButton
    _ok_cancel_layout : OkCancelLayout

    @checked
    def __init__(self : Self, angle : float, parent : QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Arc")
        self.setModal(True)
        self._dialog_layout = QVBoxLayout()
        self._angle_layout = QHBoxLayout()
        self._angle_label = QLabel("Sweep Angle:")
        self._angle_layout.addWidget(self._angle_label)
        self._angle_combo = QComboBox()
        self._angle_combo.addItems([str(angle) for angle in ANGLE_PRESETS])
        self._angle_layout.addWidget(self._angle_combo)
        self._degrees_label = QLabel("°")
        self._angle_layout.addWidget(self._degrees_label)
        self._dialog_layout.addLayout(self._angle_layout)
        self._direction_group = QGroupBox("Direction:")
        self._direction_layout = QHBoxLayout()
        self._cw_radio = QRadioButton("CW")
        self._cw_radio.setChecked(True)
        self._direction_layout.addWidget(self._cw_radio)
        self._ccw_radio = QRadioButton("CCW")
        self._direction_layout.addWidget(self._ccw_radio)
        self._direction_group.setLayout(self._direction_layout)
        self._dialog_layout.addWidget(self._direction_group)
        self._ok_cancel_layout = OkCancelLayout(self)
        self._dialog_layout.addLayout(self._ok_cancel_layout)
        self.setLayout(self._dialog_layout)

    @checked
    def getAngle(self : Self) -> float:
        try:
            abs_angle = abs(float(self._angle_combo.currentText()))
        except ValueError:
            abs_angle = 0.0
        return abs_angle if self._ccw_radio.isChecked() else -abs_angle
