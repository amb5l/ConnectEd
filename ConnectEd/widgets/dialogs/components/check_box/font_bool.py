from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QCheckBox


class FontBoolCheckBox(QCheckBox):
    def __init__(
        self   : Self,
        value  : bool    | None,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setTristate(True)
        self.setCheckState(
            Qt.CheckState.Checked   if value is True  else
            Qt.CheckState.Unchecked if value is False else
            Qt.CheckState.PartiallyChecked
        )

    def value(self : Self) -> bool | None:
        return \
            None if self.checkState() == Qt.CheckState.PartiallyChecked else \
            self.checkState() == Qt.CheckState.Checked
