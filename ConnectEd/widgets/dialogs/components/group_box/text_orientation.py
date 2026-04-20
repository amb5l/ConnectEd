from typing import Self

from PyQt6.QtWidgets import QGroupBox, QWidget

from .....core.check import checked
from .....core.types import NoChange

from ..layout.text_orientation import TextOrientationLayout


class TextOrientationGroupBox(QGroupBox):
    _layout : TextOrientationLayout

    @checked
    def __init__(
        self     : Self,
        rotation : float,
        mirror_h : bool,
        mirror_v : bool,
        autoflip : bool,
        title    : str = "Orientation",
        parent   : QWidget | None = None
    ) -> None:
        super().__init__(title, parent)
        self._layout = TextOrientationLayout(
            rotation, mirror_h, mirror_v, autoflip
        )
        self.setLayout(self._layout)

    @checked
    def getRotation(self : Self) -> float | NoChange:
        return self._layout.getRotation()

    @checked
    def getMirrorH(self : Self) -> bool | NoChange:
        return self._layout.getMirrorH()

    @checked
    def getMirrorV(self : Self) -> bool | NoChange:
        return self._layout.getMirrorV()

    @checked
    def getAutoflip(self : Self) -> bool | NoChange:
        return self._layout.getAutoflip()
