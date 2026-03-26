from typing import Self

from PyQt6.QtWidgets import QComboBox

from .....app import logger

from .....core.check import checked
from .....core.types import NoChange, NO_CHANGE

from ....graphics.properties import PropertiesMixin


class PropertyNameComboBox(QComboBox):
    _initial : str

    @checked
    def __init__(
        self  : Self,
        owner : PropertiesMixin,
        name  : str
    ) -> None:
        super().__init__()
        self._initial = name
        names = owner.properties.names()
        self.addItems(names)
        if name in names:
            self.setCurrentText(name)
        else:
            logger().warning(f"Property '{name}' not found")

    @checked
    def value(self : Self) -> str | NoChange:
        r = self.currentText()
        return r if r != self._initial else NO_CHANGE
