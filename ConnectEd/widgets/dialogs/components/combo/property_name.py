from typing import Self

from PyQt6.QtWidgets import QComboBox

from .....app import logger

from ....graphics.properties import PropertiesMixin


class PropertyNameComboBox(QComboBox):
    def __init__(
        self  : Self,
        owner : PropertiesMixin,
        name  : str
    ) -> None:
        super().__init__()
        names = owner.getPropertyNames()
        self.addItems(names)
        if name in names:
            self.setCurrentText(name)
        else:
            logger().warning(f"Property '{name}' not found")


    def getName(self : Self) -> str:
        return self.currentText()
