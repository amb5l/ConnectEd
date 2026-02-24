from typing import Self

from PyQt6.QtWidgets import QGroupBox, QWidget

from .....core.check import checked
from .....core.types import RectHandleId

from ..layout.origin import OriginLayout


class OriginGroupBox(QGroupBox):
    _layout : OriginLayout

    def __init__(
        self   : Self,
        origin : RectHandleId,
        title  : str = "Origin",
        parent : QWidget | None = None
    ) -> None:
        super().__init__(title, parent)
        self._layout = OriginLayout(origin)
        self.setLayout(self._layout)

    @checked
    def getOrigin(self : Self) -> RectHandleId:
        return self._layout.getOrigin()
