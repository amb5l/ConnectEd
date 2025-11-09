from typing import Self

from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtGui     import QFontDatabase

from ....graphics.items import NoChange, Default, DEFAULT, NO_CHANGE


class FontFamilyComboBox(QComboBox):
    def __init__(
        self      : Self,
        initial   : NoChange | Default | str,
        default   : Default | str,
        no_change : NoChange | Default | str | None = None,
        parent    : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        default_str = f" = {default}" if isinstance(default, str) else ""
        default_idx = 1
        no_change_str = \
            f" = {no_change}" if isinstance(no_change, str) else \
            f" = default{default_str}" if no_change is DEFAULT else \
            ""
        no_change_idx = 0
        self.families = []
        if no_change is not None or initial is NO_CHANGE:
            self.families.append(f"<no change{no_change_str}>")
        else:
            no_change_idx = -1
            default_idx   = 0
        self.families.append(f"<default{default_str}>")
        self.families.extend(sorted(QFontDatabase.families()))
        self.addItems(self.families)
        if initial is NO_CHANGE:
            self.setCurrentIndex(no_change_idx)
        elif initial is DEFAULT:
            self.setCurrentIndex(default_idx)
        elif isinstance(initial, str):
            self.setCurrentIndex(self.families.index(initial))

    def getChoice(self : Self) -> NoChange | Default | str:
        text = self.currentText()
        if text.startswith("<no change"):
            return NO_CHANGE
        elif text.startswith("<default"):
            return DEFAULT
        else:
            return text
