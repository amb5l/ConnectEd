from typing import Self

from PyQt6.QtCore    import Qt, QAbstractItemModel, QModelIndex
from PyQt6.QtWidgets import QStyledItemDelegate, QWidget, QLineEdit

from ....core.doc import DocBinding

from .types import NavItem, NavModel


class NavItemDelegate(QStyledItemDelegate):
    """Commit inline tree edits through ``Doc.navSetLabel``."""

    def setModelData(
        self   : Self,
        editor : QWidget,
        model  : QAbstractItemModel,
        index  : QModelIndex,
    ) -> None:
        if not isinstance(model, NavModel):
            super().setModelData(editor, model, index)
            return
        item = model.itemFromIndex(index)
        if not isinstance(item, NavItem):
            super().setModelData(editor, model, index)
            return
        binding : DocBinding | None = item.data(Qt.ItemDataRole.UserRole)
        if binding is None or isinstance(binding.subject, str):
            super().setModelData(editor, model, index)
            return
        label = editor.text() if isinstance(editor, QLineEdit) \
            else self.displayText(editor)
        if not binding.doc.navSetLabel(binding.subject, label):
            return
        super().setModelData(editor, model, index)
