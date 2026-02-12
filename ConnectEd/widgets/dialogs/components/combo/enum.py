from typing import Self, TypeVar, Generic
from enum   import Enum

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QComboBox, QWidget


T = TypeVar("T", bound=Enum)


class EnumComboBox(QComboBox, Generic[T]):
    _type : type[T]

    def __init__(
        self    : Self,
        initial : T,
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._type = type(initial)
        for member in self._type:
            self.addItem(member.value, member)
            if initial == member:
                self.setCurrentIndex(self.count() - 1)

    def value(self : Self) -> Enum:
        return self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)
