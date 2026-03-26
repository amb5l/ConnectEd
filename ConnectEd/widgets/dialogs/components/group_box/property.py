from typing import Self, Any

from PyQt6.QtWidgets import QGroupBox

from .....core.check import checked
from .....core.types import NoChange, DataKind

from ....graphics.properties import PropertiesMixin

from ..layout.property import PropertyLayout


class PropertyGroupBox(QGroupBox):
    _layout : PropertyLayout

    @checked
    def __init__(self : Self, object : PropertiesMixin, name : str) -> None:
        super().__init__()
        self.setTitle("Property")
        self._layout = PropertyLayout(object, name)
        self.setLayout(self._layout)

    @checked
    def getName(self : Self) -> str | NoChange:
        return self._layout.getName()

    @checked
    def getKind(self : Self) -> DataKind | NoChange:
        return self._layout.getKind()

    @checked
    def getValue(self : Self) -> Any | NoChange:
        return self._layout.getValue()
