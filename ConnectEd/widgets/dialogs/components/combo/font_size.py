from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox

from .....core.check import checked
from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE
from .....core.utils import val2str

from ...float import FloatDialog

from .. import CUSTOM_ICON_SIZE


class FontSizeComboBox(QComboBox):
    _SIZES = [6, 7, 8, 9, 10, 12, 14, 16, 18, 24, 36, 48, 72]

    @checked
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
        self.setIconSize(CUSTOM_ICON_SIZE)
        # build default string and value
        default_str = f" = {val2str(default)}" if isinstance(default, float) \
            else ""
        default_value = default if isinstance(default, float) else NO_CHANGE
        # build no change string and value
        no_change_str = f" = {val2str(initial)}" if isinstance(initial, float) \
            else " = default" if initial is DEFAULT \
            else ""
        no_change_value = initial if isinstance(initial, float) \
            else default_value if initial is DEFAULT \
            else NO_CHANGE
        # build custom string and value
        custom_str = no_change_str if isinstance(initial, float) \
            else default_str if initial is DEFAULT and isinstance(default, float) \
            else ""
        custom_value = initial if isinstance(initial, float) \
            else default_value if initial is DEFAULT and isinstance(default, float) \
            else None
        # add no change, default and custom entries
        if initial is NO_CHANGE:
            self.addItem(f"<no change{no_change_str}>", no_change_value)
        self.addItem(f"<default{default_str}>", default_value)
        self.addItem(f"<custom{custom_str}>", custom_value)
        # add standard entries, set current index
        self.setCurrentIndex(0)
        if initial is not NO_CHANGE and initial is not DEFAULT:
            self.setCurrentIndex(1)
        for size in self._SIZES:
            self.addItem(val2str(size), float(size))
            if initial == size:
                self.setCurrentIndex(self.count() - 1)
        # enable custom dialog
        self.activated.connect(self._onActivated)

    @checked
    def getChoice(self : Self) -> float | Default | NoChange | None:
        return self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)

    def _onActivated(self : Self, index : int) -> None:
        if self.currentText().startswith("<custom"):
            dialog = FloatDialog(title="Font Size", parent=self)
            if dialog.exec():
                s = dialog.getChoice()
                if s is not None:
                    self.setItemText(index, f"<custom = {val2str(s)}>")
                    self.setItemData(index, s, Qt.ItemDataRole.UserRole)
