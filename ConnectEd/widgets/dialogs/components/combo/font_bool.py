from typing import Self

from PyQt6.QtWidgets import QWidget, QComboBox

from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE


class FontBoolComboBox(QComboBox):
    def __init__(
        self      : Self,
        initial   : NoChange | Default | bool,
        default   : Default | bool,
        no_change : NoChange | Default | bool | None = None,
        parent    : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        default_str = \
            " = On"  if default is True else \
            " = Off" if default is False else \
            ""
        default_idx = 1
        no_change_str = \
            " = On"                    if no_change is True else \
            " = Off"                   if no_change is False else \
            f" = default{default_str}" if no_change is DEFAULT else \
            ""
        no_change_idx = 0
        if no_change is not None or initial is NO_CHANGE:
            self.addItem(f"<no change{no_change_str}>")
        else:
            no_change_idx = -1
            default_idx   = 0
        self.addItem(f"<default{default_str}>")
        self.addItem("Off")
        self.addItem("On")
        self.setCurrentIndex(
            default_idx + 2 if initial is True    else
            default_idx + 1 if initial is False   else
            default_idx     if initial is DEFAULT else
            no_change_idx
        )

    def getChoice(self : Self) -> NoChange | Default | bool | None:
        if self.currentIndex() < 0:
            return None
        if self.currentText().startswith("<no change"):
            return NO_CHANGE
        elif self.currentText().startswith("<default"):
            return DEFAULT
        else:
            return self.currentText().lower() == "on"
