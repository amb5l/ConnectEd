from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox

from .....app import logger

from .....core.check import checked
from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE


class FontBoolComboBox(QComboBox):
    _idx_default : int

    @checked
    def __init__(
        self      : Self,
        initial   : bool | Default | NoChange,
        default   : bool | NoChange,
        parent    : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        # build default string and value
        default_str = \
            "" if default is NO_CHANGE else " = On"  if default else " = Off"
        default_value = default if isinstance(default, bool) else NO_CHANGE
        # build no change string and value
        no_change_str = \
            "" if initial is NO_CHANGE else \
            " = default" if initial is DEFAULT else \
            " = On" if initial else " = Off"
        no_change_value = initial if isinstance(initial, bool) \
            else default_value if initial is DEFAULT else NO_CHANGE
        # add no change and default entries
        if initial is NO_CHANGE:
            self.addItem(f"<no change{no_change_str}>", no_change_value)
        self._idx_default = self.count()
        self.addItem(f"<default{default_str}>", default_value)
        # add standard entries, set current index
        self.setCurrentIndex(0)
        for text, value in {"On": True, "Off": False}.items():
            self.addItem(text, value)
            if initial == value:
                self.setCurrentIndex(self.count() - 1)

    @checked
    def value(self : Self) -> bool | Default | NoChange:
        return self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)

    @checked
    def setValue(self : Self, value : bool | Default | NoChange) -> None:
        if value is DEFAULT:
            index = self._idx_default
        else:
            index = self.findData(value, Qt.ItemDataRole.UserRole)
            if index < 0:
                logger().error(f"Invalid value: {value}")
                return
        self.setCurrentIndex(index)
