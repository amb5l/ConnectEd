from typing import Self

from PyQt6.QtWidgets import QComboBox, QWidget

class TextFormatComboBox(QComboBox):
    def __init__(self : Self, block : bool, parent : QWidget | None = None) -> None:
        super().__init__(parent)
        self.addItem("Line", False)
        self.addItem("Block", True)
        self.setCurrentIndex(1 if block else 0)

    def getBlock(self : Self) -> bool:
        return self.currentIndex() == 1
