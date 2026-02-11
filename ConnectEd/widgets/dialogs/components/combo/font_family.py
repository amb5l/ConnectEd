from typing import Self

from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtGui     import QFontDatabase

from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE

from .. import CUSTOM_ICON_SIZE, NoChangeIcon, DefaultIcon


class FontFamilyComboBox(QComboBox):
    def __init__(
        self    : Self,
        initial : str | Default | NoChange,
        default : str | NoChange,
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setIconSize(CUSTOM_ICON_SIZE)
        # add no change option if applicable
        if initial is NO_CHANGE:
            self.addItem("<no change>", NO_CHANGE)
            current_idx = 0
        # add default option
        if initial is DEFAULT:
            current_idx = self.count()
        default_str = f" = {default}" if isinstance(default, str) else ""
        default_value = default if isinstance(default, str) else NO_CHANGE
        self.addItem(f"<default{default_str}>", default_value)
        # add standard families
        for family in sorted(QFontDatabase.families()):
            if initial == family:
                current_idx = self.count()
            self.addItem(family, family)
        # set current index
        self.setCurrentIndex(current_idx)

    def getChoice(self : Self) -> NoChange | Default | str:
        text = self.currentText()
        if text.startswith("<no change"):
            return NO_CHANGE
        elif text.startswith("<default"):
            return DEFAULT
        else:
            return text
