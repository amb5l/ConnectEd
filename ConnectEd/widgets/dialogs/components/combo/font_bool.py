from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox

from .....app import logger

from .....core.check import checked
from .....core.types import NoChange, NO_CHANGE


class FontBoolComboBox(QComboBox):
    _initial     : bool | None | NoChange
    _idx_default : int

    @checked
    def __init__(
        self    : Self,
        value   : bool | None | NoChange,
        default : bool,
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._initial = value
        # build default string and value
        default_str = \
            "" if default is NO_CHANGE else " = On"  if default else " = Off"
        # build no change string and value
        no_change_str = \
            "" if value is NO_CHANGE else \
            " = default" if value is None else \
            " = On" if value else " = Off"
        no_change_value = value if isinstance(value, bool) \
            else None if value is None else NO_CHANGE
        # add no change and default entries
        if value is NO_CHANGE:
            self.addItem(f"<no change{no_change_str}>", no_change_value)
        self._idx_default = self.count()
        self.addItem(f"<default{default_str}>", None)
        # add standard entries, set current index
        self.setCurrentIndex(0)
        for text, v in {"On": True, "Off": False}.items():
            self.addItem(text, v)
            if value == v:
                self.setCurrentIndex(self.count() - 1)

    @checked
    def value(self : Self) -> bool | None | NoChange:
        r = self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)
        return r if r != self._initial else NO_CHANGE

    @checked
    def setValue(self : Self, value : bool | None | NoChange) -> None:
        if value is None:
            index = self._idx_default
        else:
            index = self.findData(value, Qt.ItemDataRole.UserRole)
            if index < 0:
                logger().error(f"Invalid value: {value}")
                return
        self.setCurrentIndex(index)
