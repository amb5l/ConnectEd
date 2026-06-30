from typing import Self
from types  import SimpleNamespace

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QTableView
from PyQt6.QtGui     import QStandardItemModel, QAction, QWheelEvent, QFont

from ....app import settings

from ....core.check import checked


class TableView(QTableView):
    _actions   : SimpleNamespace
    _font_size : int

    @checked
    def __init__(
        self   : Self,
        model  : QStandardItemModel,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setModel(model)
        self.resizeColumnsToContents()
        self.setFontSize(settings().get("display/font_size"))
        self._actions = SimpleNamespace()
        a = self._actions
        a.increaseTextSize = QAction("Increase Text Size", self)
        a.increaseTextSize.triggered.connect(self.increaseFontSize)
        a.decreaseTextSize = QAction("Decrease Text Size", self)
        a.decreaseTextSize.triggered.connect(self.decreaseFontSize)

    def wheelEvent(self : Self, a0 : QWheelEvent | None) -> None:
        """Handle mouse wheel events to adjust font size when Ctrl is pressed."""
        if a0 is None:
            return
        modifiers = a0.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            delta = a0.angleDelta().y()
            if delta > 0:
                self.increaseFontSize()
            elif delta < 0:
                self.decreaseFontSize()
            a0.accept()
            return
        super().wheelEvent(a0)

    @checked
    def setFontSize(self : Self, size : int) -> None:
        """Set the font size for all items in the table."""
        font = QFont()
        font.setPointSizeF(size)
        self.setFont(font)
        self._font_size = size

    def increaseFontSize(self : Self) -> None:
        """Increase the font size."""
        self.setFontSize(min(self._font_size + 1, 20)) # TODO: max from settings

    def decreaseFontSize(self : Self) -> None:
        """Decrease the font size."""
        self.setFontSize(max(self._font_size - 1, 6)) # TODO: min from settings
