from typing      import Self
from dataclasses import dataclass

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox

from .....core.check import checked
from .....core.types import NoChange, NO_CHANGE

from ..combo.rotation import RotationComboBox


class TextOrientationLayout(QVBoxLayout):
    @dataclass
    class State:
        rotation : float
        mirror_h : bool
        mirror_v : bool
        autoflip : bool

    _initial           : State
    _row1_layout       : QHBoxLayout
    _angle_label       : QLabel
    _rotation_combo    : RotationComboBox
    _autoflip_checkbox : QCheckBox
    _row2_layout       : QHBoxLayout
    _mirror_label      : QLabel
    _mirror_h_checkbox : QCheckBox
    _mirror_v_checkbox : QCheckBox

    @checked
    def __init__(
        self     : Self,
        rotation : float,
        mirror_h : bool,
        mirror_v : bool,
        autoflip : bool,
        parent   : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._initial = self.State(rotation, mirror_h, mirror_v, autoflip)
        # row 1 - rotation and autoflip
        self._row1_layout = QHBoxLayout()
        self._angle_label = QLabel("Angle:")
        self._row1_layout.addWidget(self._angle_label)
        self._rotation_combo = RotationComboBox(rotation)
        self._row1_layout.addWidget(self._rotation_combo)
        self._autoflip_checkbox = QCheckBox("Auto Flip")
        self._autoflip_checkbox.setChecked(autoflip)
        self._row1_layout.addWidget(self._autoflip_checkbox)
        self.addLayout(self._row1_layout)
        # row 2 - mirror horizontal and vertical
        self._row2_layout = QHBoxLayout()
        self._mirror_label = QLabel("Mirror:")
        self._row2_layout.addWidget(self._mirror_label)
        self._mirror_h_checkbox = QCheckBox("Horizontal")
        self._mirror_h_checkbox.setChecked(mirror_h)
        self._row2_layout.addWidget(self._mirror_h_checkbox)
        self._mirror_v_checkbox = QCheckBox("Vertical")
        self._mirror_v_checkbox.setChecked(mirror_v)
        self._row2_layout.addWidget(self._mirror_v_checkbox)
        self.addLayout(self._row2_layout)

    @checked
    def getRotation(self : Self) -> float | NoChange:
        r = self._rotation_combo.value()
        return r if r != self._initial.rotation else NO_CHANGE

    @checked
    def getMirrorH(self : Self) -> bool | NoChange:
        r = self._mirror_h_checkbox.isChecked()
        return r if r != self._initial.mirror_h else NO_CHANGE

    @checked
    def getMirrorV(self : Self) -> bool | NoChange:
        r = self._mirror_v_checkbox.isChecked()
        return r if r != self._initial.mirror_v else NO_CHANGE

    @checked
    def getAutoflip(self : Self) -> bool | NoChange:
        r = self._autoflip_checkbox.isChecked()
        return r if r != self._initial.autoflip else NO_CHANGE
