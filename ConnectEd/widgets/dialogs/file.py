from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QDialog, QFileDialog, \
                            QVBoxLayout, QListWidget, QListWidgetItem

from ...app import session

from ...core.check   import checked
from ...core.defs    import LIB_EXT, DSN_EXT
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
        self.setWindowTitle("New")
        self.setModal(True)
        self._layout = QVBoxLayout()
        self._doc_types = session().docTypes()
        self._list_widget = QListWidget()
        self._list_widget.setSelectionMode(
            QListWidget.SelectionMode.SingleSelection
        )
        for doc_type in self._doc_types:
            item = QListWidgetItem(doc_type.name)
            item.setData(Qt.ItemDataRole.UserRole, doc_type)
            self._list_widget.addItem(item)
        self._list_widget.itemSelectionChanged.connect(self._updateOkEnabled)
        self._layout.addWidget(self._list_widget)
        self._ok_cancel_layout = OkCancelLayout(self)
        self._layout.addLayout(self._ok_cancel_layout)
        self.setLayout(self._layout)
        self._updateOkEnabled()

    @checked
    def docType(self : Self) -> DocType | None:
        item = self._list_widget.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    @checked
    def _updateOkEnabled(self : Self) -> None:
        self._ok_cancel_layout._ok_button.setEnabled(
            self._list_widget.currentItem() is not None
        )


class FileOpenDialog(QFileDialog):
    @checked
    def __init__(self : Self, parent : QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Open")
        self.setFileMode(QFileDialog.FileMode.ExistingFiles)
        filters = [
            f"{doc_type.name} (*{doc_type.ext})"
            for doc_type in session().docTypes()
        ]
        self.setNameFilter(";;".join(filters))
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)


class FileSaveAsDialog(QFileDialog):
    @checked
    def __init__(
        self   : Self,
        kind   : str,
        parent : QWidget | None = None
    ) -> None:
        match kind:
            case "Design":
                name_filter    = f"Connected Designs (*{DSN_EXT})"
                default_suffix = DSN_EXT
            case "Library":
                name_filter    = f"Connected Libraries (*{LIB_EXT})"
                default_suffix = LIB_EXT
            case _:
                raise ValueError(f"Unknown type name: {kind}")
        super().__init__(parent)
        self.setWindowTitle(f"Save {kind} As")
        self.setFileMode(QFileDialog.FileMode.AnyFile)
        self.setNameFilter(name_filter)
        self.setDefaultSuffix(default_suffix)
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
