from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import QItemSelection
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableView, QPushButton, QHBoxLayout,
    QAbstractItemView,
)
from PyQt6.QtGui     import QStandardItemModel, QStandardItem

from ...core.check import checked

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...domains.hdl.schematic.library import HdlSchematicLibrary
    from .browser                         import LibraryBrowser


class LibraryPropertiesPane(QWidget):
    _library       : HdlSchematicLibrary
    _layout        : QVBoxLayout
    _model         : QStandardItemModel
    _title         : QLabel
    _table         : QTableView
    _buttons       : QHBoxLayout
    _new_button    : QPushButton
    _delete_button : QPushButton

    @checked
    def __init__(
        self    : Self,
        library : HdlSchematicLibrary,
        parent  : LibraryBrowser | None = None
    ) -> None:
        super().__init__(parent)
        self._library = library
        self._layout = QVBoxLayout()
        # title
        self._title = QLabel("Properties")
        self._layout.addWidget(self._title)
        # table
        self._model = QStandardItemModel()
        for name, (kind, value) in library.getPropertyDefaults().items():
            name_item = QStandardItem(name)
            kind_item = QStandardItem(kind.value)
            value_item = QStandardItem(value)
            self._model.appendRow([name_item, kind_item, value_item])
        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._layout.addWidget(self._table)
        # buttons
        self._buttons = QHBoxLayout()
        self._new_button = QPushButton("New")
        self._buttons.addWidget(self._new_button)
        self._delete_button = QPushButton("Delete")
        self._delete_button.setEnabled(False)
        self._buttons.addWidget(self._delete_button)
        self._buttons.addStretch()
        self._layout.addLayout(self._buttons)
        # layout
        self.setLayout(self._layout)
        # connect table selection to delete button
        selection = self._table.selectionModel()
        if selection is not None:
            selection.selectionChanged.connect(self._onSelectionChanged)

    @checked
    def _onSelectionChanged(
        self       : Self,
        selected   : QItemSelection,
        deselected : QItemSelection,
    ) -> None:
        selection = self._table.selectionModel()
        has_row = selection is not None and bool(selection.selectedRows())
        self._delete_button.setEnabled(has_row)
