from typing import Self

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QCheckBox

from .....core.check import checked
from .....core.types import NoChange, NO_CHANGE

from ..combo.rotation import RotationComboBox


class TextRotationLayout(QHBoxLayout):
    _initial_flip   : bool
    _angle_label    : QLabel
    _rotation_combo : RotationComboBox
    _flip_checkbox  : QCheckBox

    @checked
    def __init__(
        self     : Self,
        rotation : float,
        flip     : bool,
        parent   : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._initial_flip = flip
        self._angle_label = QLabel("Angle:")
        self.addWidget(self._angle_label)
        self._rotation_combo = RotationComboBox(rotation)
        self.addWidget(self._rotation_combo)
        self._flip_checkbox = QCheckBox("Flip")
        self._flip_checkbox.setChecked(flip)
        self.addWidget(self._flip_checkbox)

    @checked
    def getRotation(self : Self) -> float | NoChange:
        return self._rotation_combo.value()

    @checked
    def getFlip(self : Self) -> bool | NoChange:
        r = self._flip_checkbox.isChecked()
        return r if r != self._initial_flip else NO_CHANGE
