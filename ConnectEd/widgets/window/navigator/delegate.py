from typing import Self

from PyQt6.QtCore    import Qt, QAbstractItemModel, QModelIndex
from PyQt6.QtWidgets import QStyledItemDelegate, QWidget, QLineEdit

from ....core.doc import DocBinding

from .types import NavItem, NavModel


class NavItemDelegate(QStyledItemDelegate):
    """Commit inline tree edits through ``Doc.navSetLabel``."""

    def setModelData(
        self   : Self,
        editor : QWidget | None,
        model  : QAbstractItemModel | None,
        index  : QModelIndex,
    ) -> None:
        if not isinstance(model, NavModel):
            super().setModelData(editor, model, index)
            return
        if not isinstance(item := model.itemFromIndex(index), NavItem):
            super().setModelData(editor, model, index)
            return
        binding : DocBinding | None = item.data(Qt.ItemDataRole.UserRole)
        if binding is None or isinstance(binding.subject, str):
            super().setModelData(editor, model, index)
            return
        if not isinstance(editor, QLineEdit):
            super().setModelData(editor, model, index)
            return
        if not binding.doc.navSetLabel(binding.subject, editor.text()):
            return
        super().setModelData(editor, model, index)
