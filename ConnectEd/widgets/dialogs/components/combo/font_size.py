from typing import Self

from PyQt6.QtWidgets import QWidget, QComboBox

from ....graphics.items import NoChange, Default, DEFAULT, NO_CHANGE


class FontSizeComboBox(QComboBox):
    SIZES : list[float] = [6, 7, 8, 9, 10, 12, 14, 16, 18, 24, 36, 48, 72]

    sizes : list[str | float]

    def __init__(
        self      : Self,
        initial   : NoChange | Default | float | int,
        default   : Default | float | int,
        no_change : NoChange | Default | float | int | None = None,
        parent    : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        default_str = \
            f" = {default}" if isinstance(default, float | int) else ""
        default_idx = 1
        no_change_str = \
            f" = {no_change}" if isinstance(no_change, float | int) else \
            f" = default{default_str}" if no_change is DEFAULT else \
            ""
        no_change_idx = 0
        self.sizes = []
        if no_change is not None or initial is NO_CHANGE:
            self.sizes.append(f"<no change{no_change_str}>")
        else:
            no_change_idx = -1
            default_idx   = 0
        self.sizes.append(f"<default{default_str}>")
        self.sizes.extend([str(size) for size in self.SIZES])
        self.addItems(self.sizes)
        if initial is NO_CHANGE:
            self.setCurrentIndex(no_change_idx)
        elif initial is DEFAULT:
            self.setCurrentIndex(default_idx)
        elif isinstance(initial, float | int) and initial in self.SIZES:
            size_str = str(int(initial) if initial == int(initial) else initial)
            if size_str in self.sizes:
                self.setCurrentIndex(self.sizes.index(size_str))
            else:
                self.setCurrentIndex(default_idx)

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
