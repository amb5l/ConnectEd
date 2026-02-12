from typing import Self
from enum   import Enum

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QComboBox, QWidget

class EnumComboBox(QComboBox):
    _type : type[Enum]

    def __init__(
        self    : Self,
        initial : Enum,
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._type = type(initial)
        for member in self._type:
            self.addItem(member.value, member)

    def getChoice(self : Self) -> Enum:
        return self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)
