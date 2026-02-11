from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox

from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE
from .....core.utils import val2str

from ...float import FloatDialog


class FontSizeComboBox(QComboBox):
    _SIZES = [6, 7, 8, 9, 10, 12, 14, 16, 18, 24, 36, 48, 72]

    def __init__(
        self    : Self,
        initial : float | int | Default | NoChange,
        default : float | int | NoChange,
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        if isinstance(initial, int):
            initial = float(initial)
        if isinstance(default, int):
            default = float(default)
        # add no change option if applicable
        if initial is NO_CHANGE:
            self.addItem("<no change>", NO_CHANGE)
            current_idx = 0
        # add default option
        if initial is DEFAULT:
            current_idx = self.count()
        default_str = f" = {val2str(default)}" if isinstance(default, float) \
            else ""
        default_value = default if isinstance(default, float) else NO_CHANGE
        self.addItem(f"<default{default_str}>", default_value)
        # add custom option
        if isinstance(initial, float):
            current_idx = self.count()
        custom_str = f" = {val2str(initial)}" if isinstance(initial, float) \
            else default_str if isinstance(default, float) \
            else ""
        custom_value = initial if isinstance(initial, float) \
            else default if isinstance(default, float) \
            else None
        self.addItem(f"<custom{custom_str}>", custom_value)
        # add standard widths
        for size in self._SIZES:
            if initial == size:
                current_idx = self.count()
            self.addItem(val2str(size), float(size))
        # set current index
        self.setCurrentIndex(current_idx)
        self.activated.connect(self._onActivated)

    def getChoice(self : Self) -> NoChange | Default | float | None:
        return self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)

    def _onActivated(self : Self, index : int) -> None:
        if self.currentText().startswith("<custom"):
            dialog = FloatDialog(title="Font Size", parent=self)
            if dialog.exec():
                s = dialog.getChoice()
                if s is not None:
                    self.setItemText(index, f"<custom = {val2str(s)}>")
                    self.setItemData(index, s, Qt.ItemDataRole.UserRole)
