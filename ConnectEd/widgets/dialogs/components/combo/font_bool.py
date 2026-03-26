from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox

from .....app import logger

from .....core.check import checked
from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE, FontBool


class FontBoolComboBox(QComboBox):
    _initial     : FontBool | NoChange
    _idx_default : int

    @checked
    def __init__(
        self    : Self,
        value   : FontBool | NoChange,
        default : bool | NoChange,
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
            " = default" if value == DEFAULT else \
            " = On" if value else " = Off"
        no_change_value = value if isinstance(value, bool) \
            else DEFAULT if value == DEFAULT else NO_CHANGE
        # add no change and default entries
        if value is NO_CHANGE:
            self.addItem(f"<no change{no_change_str}>", no_change_value)
        self._idx_default = self.count()
        self.addItem(f"<default{default_str}>", DEFAULT)
        # add standard entries, set current index
        self.setCurrentIndex(0)
        for text, v in {"On": True, "Off": False}.items():
            self.addItem(text, v)
            if value == v:
                self.setCurrentIndex(self.count() - 1)

    @checked
    def value(self : Self) -> FontBool | NoChange:
        r = self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)
        return r if r != self._initial else NO_CHANGE

    @checked
    def setValue(self : Self, value : FontBool | NoChange) -> None:
        if value == DEFAULT:
            index = self._idx_default
        else:
            index = self.findData(value, Qt.ItemDataRole.UserRole)
            if index < 0:
                logger().error(f"Invalid value: {value}")
                return
        self.setCurrentIndex(index)
