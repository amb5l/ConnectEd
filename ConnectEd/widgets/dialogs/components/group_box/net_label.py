from typing import Self

from PyQt6.QtWidgets import QGroupBox

from .....core.check import checked
from .....core.types import NoChange

from ..layout.net_label import NetLabelItemLayout


class NetLabelItemGroupBox(QGroupBox):
    _layout : NetLabelItemLayout

    @checked
    def __init__(
        self  : Self,
        name  : str,
        value : str
    ) -> None:
        super().__init__()
        self.setTitle("Net Label")
        self._layout = NetLabelItemLayout(name, value)
        self.setLayout(self._layout)

    @checked
    def getName(self : Self) -> str | NoChange:
        return self._layout.getName()

    @checked
    def getValue(self : Self) -> str | NoChange:
        return self._layout.getValue()
