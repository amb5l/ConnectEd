from typing import Self

from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtGui     import QFontDatabase

from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE


class FontFamilyComboBox(QComboBox):
    def __init__(
        self    : Self,
        initial : str | Default | NoChange,
        default : str | NoChange,
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        # build default string and value
        default_str = f" = {default}" if isinstance(default, str) else ""
        default_value = default if isinstance(default, str) else NO_CHANGE
        # build no change string and value
        no_change_str = f" = {initial}" if isinstance(initial, str) else ""
        no_change_value = initial if isinstance(initial, str) \
            else default_value if initial is DEFAULT \
            else NO_CHANGE
        # add no change and default entries
        if initial is NO_CHANGE:
            self.addItem(f"<no change{no_change_str}>", no_change_value)
        self.addItem(f"<default{default_str}>", default_value)
        # add standard entries, set current index
        self.setCurrentIndex(0)
        if initial is not NO_CHANGE and initial is not DEFAULT:
            self.setCurrentIndex(1)
        for family in sorted(QFontDatabase.families()):
            self.addItem(family, family)
            if initial == family:
                self.setCurrentIndex(self.count() - 1)

    def getChoice(self : Self) -> NoChange | Default | str:
        text = self.currentText()
        if text.startswith("<no change"):
            return NO_CHANGE
        elif text.startswith("<default"):
            return DEFAULT
        else:
            return text
