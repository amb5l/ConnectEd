from typing import Self

from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtGui     import QFontDatabase

from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE


class FontFamilyComboBox(QComboBox):
    def __init__(
        self      : Self,
        initial   : NoChange | Default | str,
        default   : Default | str,
        parent    : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        # Determine default string
        default_str = f" = {default}" if isinstance(default, str) else ""
        # Determine no_change string from initial
        if isinstance(initial, str):
            no_change_str = f" = {initial}"
        elif initial is DEFAULT:
            no_change_str = f" = default{default_str}"
        else:  # NO_CHANGE
            no_change_str = ""
        # Build items list
        self.families = []
        self.families.append(f"<no change{no_change_str}>")
        self.families.append(f"<default{default_str}>")
        self.families.extend(sorted(QFontDatabase.families()))
        self.addItems(self.families)
        # Set initial selection
        if initial is NO_CHANGE:
            self.setCurrentIndex(0)
        elif initial is DEFAULT:
            self.setCurrentIndex(1)
        elif isinstance(initial, str) and initial in self.families:
            self.setCurrentIndex(self.families.index(initial))

    def getChoice(self : Self) -> NoChange | Default | str:
        text = self.currentText()
        if text.startswith("<no change"):
            return NO_CHANGE
        elif text.startswith("<default"):
            return DEFAULT
        else:
            return text
