from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtGui     import QFontDatabase

from .....app import logger

from .....core.check import checked
from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE


class FontFamilyComboBox(QComboBox):
    _idx_default : int

    @checked
    def __init__(
        self    : Self,
        value   : str | Default | NoChange,
        default : str | NoChange,
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        # build default string and value
        default_str = f" = {default}" if isinstance(default, str) else ""
        default_value = default if isinstance(default, str) else NO_CHANGE
        # build no change string and value
        no_change_str = f" = {value}" if isinstance(value, str) else ""
        no_change_value = value if isinstance(value, str) \
            else default_value if value is DEFAULT \
            else NO_CHANGE
        # add no change and default entries
        if value is NO_CHANGE:
            self.addItem(f"<no change{no_change_str}>", no_change_value)
        self._idx_default = self.count()
        self.addItem(f"<default{default_str}>", default_value)
        # add standard entries, set current index
        self.setCurrentIndex(0)
        if value is not NO_CHANGE and value is not DEFAULT:
            self.setCurrentIndex(1)
        for family in sorted(QFontDatabase.families()):
            self.addItem(family, family)
            if value == family:
                self.setCurrentIndex(self.count() - 1)

    @checked
    def value(self : Self) -> str | Default | NoChange:
        return self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)

    @checked
    def setValue(self : Self, value : str | Default) -> None:
        if value is DEFAULT:
            index = self._idx_default
        else:
            index = self.findData(value, Qt.ItemDataRole.UserRole)
            if index < 0:
                logger().error(f"Invalid value: {value}")
                return
        self.setCurrentIndex(index)
