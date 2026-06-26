from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtGui     import QStandardItem, QStandardItemModel, QBrush, QPalette
from PyQt6.QtWidgets import QApplication

from ....core.check import checked


class NavItem(QStandardItem):
    pass


class NavDummyItem(QStandardItem):
    @checked
    def __init__(self : Self, text : str) -> None:
        super().__init__(text)
        font = self.font()
        font.setItalic(True)
        self.setFont(font)
        self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsEditable)
        palette = QApplication.palette()
        self.setForeground(QBrush(
            palette.color(
                QPalette.ColorGroup.Disabled,
                QPalette.ColorRole.PlaceholderText,
            )
        ))


class NavModel(QStandardItemModel):
    pass
