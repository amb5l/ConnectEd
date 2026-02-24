from typing import Self

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QCheckBox

from .....core.check import checked

from ..combo.angle import AngleComboBox


class RotationLayout(QHBoxLayout):
    _angle_label         : QLabel
    _angle_combo         : AngleComboBox
    _compensate_checkbox : QCheckBox

    @checked
    def __init__(
        self      : Self,
        rot_angle : float,
        rot_comp  : bool,
        parent    : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._angle_label = QLabel("Angle:")
        self.addWidget(self._angle_label)
        self._angle_combo = AngleComboBox(rot_angle)
        self.addWidget(self._angle_combo)
        self._compensate_checkbox = QCheckBox("Compensate")
        self._compensate_checkbox.setChecked(rot_comp)
        self.addWidget(self._compensate_checkbox)

    @checked
    def getRotAngle(self : Self) -> float:
        return self._angle_combo.getAngle()

    @checked
    def getRotComp(self : Self) -> bool:
        return self._compensate_checkbox.isChecked()
