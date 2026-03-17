from typing import Self

from PyQt6.QtWidgets import QGroupBox, QWidget

from .....core.check import checked

from ..layout.text_rotation import TextRotationLayout


class TextRotationGroupBox(QGroupBox):
    _layout : TextRotationLayout

    @checked
    def __init__(
        self     : Self,
        rotation : float,
        flip     : bool,
        title    : str = "Rotation",
        parent   : QWidget | None = None
    ) -> None:
        super().__init__(title, parent)
        self._layout = TextRotationLayout(rotation, flip)
        self.setLayout(self._layout)

    @checked
    def getRotation(self : Self) -> float:
        return self._layout.getRotation()

    @checked
    def getFlip(self : Self) -> bool:
        return self._layout.getFlip()
