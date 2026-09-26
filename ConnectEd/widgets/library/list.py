from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QPushButton,
)

from ...core.check import checked

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...domains.hdl.schematic.library import HdlSchematicLibrary
    from ...widgets.graphics.items.symbol import SymbolDefinitionItem
    from .browser                         import LibraryBrowser


class LibraryListPane(QWidget):
    _library       : HdlSchematicLibrary
    _layout        : QVBoxLayout
    _title         : QLabel
    _list          : QListWidget
    _buttons       : QHBoxLayout
    _new_button    : QPushButton
    _delete_button : QPushButton

    selectionChanged = pyqtSignal(object)  # noqa: N815

    @checked
    def __init__(
        self    : Self,
        library : HdlSchematicLibrary,
        parent  : LibraryBrowser | None = None
    ) -> None:
        super().__init__(parent)
        self._library = library
        self._layout = QVBoxLayout(self)
        # title
        self._title = QLabel("Symbols")
        self._layout.addWidget(self._title)
        # list
        self._list = QListWidget()
        for symbol in library.getSymbols().values():
            item = QListWidgetItem(symbol.name())
            item.setData(Qt.ItemDataRole.UserRole, symbol)
            self._list.addItem(item)
        self._layout.addWidget(self._list)
        # buttons
        self._buttons = QHBoxLayout()
        self._new_button = QPushButton("New")
        self._buttons.addWidget(self._new_button)
        self._delete_button = QPushButton("Delete")
        self._delete_button.setEnabled(False)
        self._buttons.addWidget(self._delete_button)
        self._buttons.addStretch()
        self._layout.addLayout(self._buttons)
        self._list.itemSelectionChanged.connect(self._onItemSelectionChanged)

    @checked
    def currentItem(self : Self) -> SymbolDefinitionItem | None:
        item = self._list.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    @checked
    def _onItemSelectionChanged(self : Self) -> None:
        self._delete_button.setEnabled(bool(self._list.selectedItems()))
        self.selectionChanged.emit(self.currentItem())

    def _onNewButtonClicked(self : Self) -> None:
        raise NotImplementedError("Not implemented")
