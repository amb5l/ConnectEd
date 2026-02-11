from typing import Self

from PyQt6.QtWidgets import QWidget, QComboBox

from .....core.types import Edge


class EdgeComboBox(QComboBox):
    def __init__(self : Self,
        edge   : Edge,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.addItems([e.value for e in Edge])

    def getChoice(self : Self) -> Edge:
        return Edge(self.currentText())
