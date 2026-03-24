from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox

from .....app import logger

from .....core.check import checked
from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE
from .....core.utils import val2str

from ...float import FloatDialog

from .. import customIconSize


class FontSizeComboBox(QComboBox):
    _SIZES = [6, 7, 8, 9, 10, 12, 14, 16, 18, 24, 36, 48, 72]

    _idx_default : int
    _idx_custom  : int

    @checked
    def __init__(
        self    : Self,
        value   : float | int | Default | NoChange,
        default : float | int | NoChange,
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        if isinstance(value, int):
            value = float(value)
        if isinstance(default, int):
            default = float(default)
        self.setIconSize(customIconSize())
        # build default string and value
        default_str = f" = {val2str(default)}" if isinstance(default, float) \
            else ""
        default_value = default if isinstance(default, float) else NO_CHANGE
        # build no change string and value
        no_change_str = f" = {val2str(value)}" if isinstance(value, float) \
            else " = default" if value == DEFAULT \
            else ""
        no_change_value = value if isinstance(value, float) \
            else default_value if value == DEFAULT \
            else NO_CHANGE
        # build custom string and value
        custom_str = no_change_str if isinstance(value, float) \
            else default_str if value == DEFAULT and isinstance(default, float) \
            else ""
        custom_value = value if isinstance(value, float) \
            else default_value if value == DEFAULT and isinstance(default, float) \
            else None
        # add no change, default and custom entries
        if value is NO_CHANGE:
            self.addItem(f"<no change{no_change_str}>", no_change_value)
        self._idx_default = self.count()
        self.addItem(f"<default{default_str}>", default_value)
        self._idx_custom = self.count()
        self.addItem(f"<custom{custom_str}>", custom_value)
        # add standard entries, set current index
        self.setCurrentIndex(0)
        if value is not NO_CHANGE and value != DEFAULT:
            self.setCurrentIndex(1)
        for size in self._SIZES:
            self.addItem(val2str(size), float(size))
            if value == size:
                self.setCurrentIndex(self.count() - 1)
        # enable custom dialog
        self.activated.connect(self._onActivated)

    @checked
    def value(self : Self) -> float | Default | NoChange:
        return self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)

    @checked
    def setValue(self : Self, value : float | Default) -> None:
        if value == DEFAULT:
            index = self._idx_default
        else:
            index = self.findData(value, Qt.ItemDataRole.UserRole)
            if index < 0:
                index = self._idx_custom
                self.setItemText(index, f"<custom = {val2str(value)}>")
                self.setItemData(index, value, Qt.ItemDataRole.UserRole)
        self.setCurrentIndex(index)

    def _onActivated(self : Self, index : int) -> None:
        if self.currentText().startswith("<custom"):
            dialog = FloatDialog(title="Font Size", parent=self)
            if dialog.exec():
                s = dialog.value()
                if s is not None:
                    self.setItemText(index, f"<custom = {val2str(s)}>")
                    self.setItemData(index, s, Qt.ItemDataRole.UserRole)
