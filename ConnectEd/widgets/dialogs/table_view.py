from typing import Self, Optional
from types  import SimpleNamespace

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QTableView
from PyQt6.QtGui     import QStandardItemModel, QAction, QWheelEvent, QFont

from ...app import settings


class TableView(QTableView):
    actions   : SimpleNamespace
    font_size : int

    def __init__(
        self   : Self,
        model  : QStandardItemModel,
        parent : Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.setModel(model)
        self.resizeColumnsToContents()
        self.setFontSize(settings().get("display/font_size"))
        self.actions = SimpleNamespace()
        a = self.actions
        a.increaseTextSize = QAction("Increase Text Size", self)
        a.increaseTextSize.triggered.connect(self.increaseFontSize)
        a.decreaseTextSize = QAction("Decrease Text Size", self)
        a.decreaseTextSize.triggered.connect(self.decreaseFontSize)

    def wheelEvent(self : Self, event: QWheelEvent) -> None:
        """Handle mouse wheel events to adjust font size when Ctrl is pressed."""
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.increaseFontSize()
            elif delta < 0:
                self.decreaseFontSize()
            event.accept()
            return
        super().wheelEvent(event)

    def setFontSize(self : Self, size : int) -> None:
        """Set the font size for all items in the table."""
        font = QFont()
        font.setPointSizeF(size)
        self.setFont(font)
        self.font_size = size

    def increaseFontSize(self : Self) -> None:
        """Increase the font size."""
        self.setFontSize(min(self.font_size + 1, 20)) # TODO: max from settings

    def decreaseFontSize(self : Self) -> None:
        """Decrease the font size."""
        self.setFontSize(max(self.font_size - 1, 6)) # TODO: min from settings
