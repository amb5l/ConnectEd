from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...app import session

from ...core.check   import checked
from ...core.session import DocType

from .components.layout.ok_cancel import OkCancelLayout


class FileNewDialog(QDialog):
    """Displays list of registered document types."""

    _layout           : QVBoxLayout
    _list_widget      : QListWidget
    _ok_cancel_layout : OkCancelLayout

    @checked
    def __init__(
        self   : Self,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("New Document")
        self.setModal(True)
        self._layout = QVBoxLayout()
        self._doc_types = session().docTypes()
        self._list_widget = QListWidget()
        # NoSelection avoids Qt painting a current-row highlight before click
        self._list_widget.setSelectionMode(
            QListWidget.SelectionMode.NoSelection
        )
        for doc_type in self._doc_types:
            item = QListWidgetItem(doc_type.name)
            item.setData(Qt.ItemDataRole.UserRole, doc_type)
            self._list_widget.addItem(item)
        self._list_widget.itemClicked.connect(self._onListItemClicked)
        self._list_widget.itemDoubleClicked.connect(self._onListItemDoubleClicked)
        self._layout.addWidget(self._list_widget)
        self._ok_cancel_layout = OkCancelLayout(self)
        self._layout.addLayout(self._ok_cancel_layout)
        self.setLayout(self._layout)
        self._updateOkEnabled()
        self._ok_cancel_layout._cancel_button.setFocus()

    @checked
    def docType(self : Self) -> DocType | None:
        items = self._list_widget.selectedItems()
        if not items:
            return None
        return items[0].data(Qt.ItemDataRole.UserRole)

    @checked
    def _onListItemClicked(self : Self, item : QListWidgetItem) -> None:
        self._list_widget.setSelectionMode(
            QListWidget.SelectionMode.SingleSelection
        )
        self._list_widget.setCurrentItem(item)
        item.setSelected(True)
        self._updateOkEnabled()

    @checked
    def _onListItemDoubleClicked(self : Self, item : QListWidgetItem) -> None:
        self._onListItemClicked(item)
        self.accept()

    @checked
    def _updateOkEnabled(self : Self) -> None:
        self._ok_cancel_layout._ok_button.setEnabled(
            bool(self._list_widget.selectedItems())
        )


class FileOpenDialog(QFileDialog):
    @checked
    def __init__(
        self     : Self,
        parent   : QWidget | None = None,
        doc_type : DocType | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Open")
        self.setFileMode(QFileDialog.FileMode.ExistingFiles)
        filters = session().fileFilters(doc_type)
        self.setNameFilter(
            filters[0] if len(filters) == 1 else ";;".join(filters)
        )
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)


class FileSaveAsDialog(QFileDialog):
    @checked
    def __init__(
        self     : Self,
        doc_type : DocType,
        parent   : QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Save {doc_type.name} As")
        self.setFileMode(QFileDialog.FileMode.AnyFile)
        self.setNameFilter(f"{doc_type.name} (*{doc_type.fileExt})")
        self.setDefaultSuffix(doc_type.fileExt.removeprefix("."))
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
