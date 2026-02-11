from typing import Self

from PyQt6.QtWidgets import QWidget, QComboBox

from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE


class FontSizeComboBox(QComboBox):
    SIZES : list[float] = [6, 7, 8, 9, 10, 12, 14, 16, 18, 24, 36, 48, 72]

    sizes : list[str | float]

    def __init__(
        self      : Self,
        initial   : NoChange | Default | float | int,
        default   : Default | float | int,
        parent    : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        # Determine default string
        default_str = \
            f" = {default}" if isinstance(default, float | int) else ""
        # Determine no_change string from initial
        if isinstance(initial, float | int):
            no_change_str = f" = {initial}"
        elif initial is DEFAULT:
            no_change_str = f" = default{default_str}"
        else:  # NO_CHANGE
            no_change_str = ""
        # Build items list
        self.sizes = []
        self.sizes.append(f"<no change{no_change_str}>")
        self.sizes.append(f"<default{default_str}>")
        self.sizes.extend([str(size) for size in self.SIZES])
        self.addItems(self.sizes)
        # Set initial selection
        if initial is NO_CHANGE:
            self.setCurrentIndex(0)
        elif initial is DEFAULT:
            self.setCurrentIndex(1)
        elif isinstance(initial, float | int):
            size_str = str(int(initial) if initial == int(initial) else initial)
            if size_str in self.sizes:
                self.setCurrentIndex(self.sizes.index(size_str))
            else:
                self.setCurrentIndex(1)  # default

    def getChoice(self : Self) -> NoChange | Default | float | None:
        text = self.currentText()
        if text.startswith("<no change"):
            return NO_CHANGE
        elif text.startswith("<default"):
            return DEFAULT
        else:
            try:
                return float(text)
            except ValueError:
                return None
