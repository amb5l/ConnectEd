from typing import Self, TypeVar, Generic
from enum   import Enum

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QComboBox, QWidget

from .....app import logger

from .....core.check import checked
from .....core.types import NoChange, NO_CHANGE
from .....core.utils import val2str


T = TypeVar("T", bound=Enum)


class EnumComboBox(QComboBox, Generic[T]):
    _type    : type[T]
    _initial : T

    @checked
    def __init__(
        self   : Self,
        value  : T,
        subset : tuple[T, ...] | None = None,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._type = type(value)
        self._initial = value
        for member in self._type:
            if subset is not None and member not in subset:
                continue
            self.addItem(val2str(member), member)
            if value == member:
                self.setCurrentIndex(self.count() - 1)

    @checked
    def raw(self : Self) -> T:
        return self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)

    @checked
    def value(self : Self) -> T | NoChange:
        r = self.raw()
        return r if r != self._initial else NO_CHANGE

    @checked
    def setValue(self : Self, value : T) -> None:
        index = self.findData(value, Qt.ItemDataRole.UserRole)
        if index < 0:
            logger().error(f"Invalid value: {value}")
            return
        self.setCurrentIndex(index)
