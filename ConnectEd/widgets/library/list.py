from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, \
                            QListWidget, QListWidgetItem

from ...core.check import checked

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...domains.hdl.schematic.library import HdlSchematicLibrary
    from ...widgets.graphics.items.symbol import SymbolDefinitionItem
    from .browser import LibraryBrowser


class LibraryListPane(QWidget):
    _library : HdlSchematicLibrary
    _layout  : QVBoxLayout
    _title   : QLabel
    _list    : QListWidget

    selectionChanged = pyqtSignal(object) # noqa: N815

    def __init__(
        self    : Self,
        library : HdlSchematicLibrary,
        parent  : LibraryBrowser | None = None
    ) -> None:
        super().__init__(parent)
        self._library = library
        self._layout = QVBoxLayout(self)
        # title
        self._title = QLabel("Definitions")
        self._layout.addWidget(self._title)
        # list
        self._list = QListWidget()
        for symbol in library.getSymbols().values():
            item = QListWidgetItem(symbol.name())
            item.setData(Qt.ItemDataRole.UserRole, symbol)
            self._list.addItem(item)
        self._layout.addWidget(self._list)
        self._list.itemSelectionChanged.connect(self._onItemSelectionChanged)

    @checked
    def currentItem(self : Self) -> SymbolDefinitionItem | None:
        item = self._list.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    @checked
    def _onItemSelectionChanged(self : Self) -> None:
        self.selectionChanged.emit(self.currentItem())
