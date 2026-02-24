from typing import Self

from PyQt6.QtWidgets import QGroupBox, QWidget

from .....core.check import checked

from ..layout.rotation import RotationLayout


class RotationGroupBox(QGroupBox):
    _layout : RotationLayout

    @checked
    def __init__(
        self      : Self,
        rot_angle : float,
        rot_comp  : bool,
        title     : str = "Rotation",
        parent    : QWidget | None = None
    ) -> None:
        super().__init__(title, parent)
        self._layout = RotationLayout(rot_angle, rot_comp)
        self.setLayout(self._layout)

    @checked
    def getRotAngle(self : Self) -> float:
        return self._layout.getRotAngle()

    @checked
    def getRotComp(self : Self) -> bool:
        return self._layout.getRotComp()
