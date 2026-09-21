from __future__ import annotations

from typing import Self, Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QStandardItem, QBrush

from ...app import settings

from ...core.check import checked
from ...core.types import NoChange
from ...core.utils import val2str


class TableItem(QStandardItem):
    _IDX_INITIAL = 0
    _IDX_CURRENT = 1
    _IDX_DELETED = 2

    @checked
    def __init__(
        self     : Self,
        value    : Any,
        new      : bool = False,
        editable : bool = True,
        enabled  : bool = True
    ) -> None:
        super().__init__()
        self.setDeleted(False)
        self.setInitial(None if new else value)
        self.setEnabled(enabled)
        self.setEditable(editable)
        self.setValue(value)

    @checked
    def initial(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_INITIAL)

    @checked
    def setInitial(self : Self, value : Any) -> None:
        self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_INITIAL)

    @checked
    def value(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_CURRENT)

    @checked
    def setValue(self : Self, value : Any | NoChange) -> None:
        if isinstance(value, NoChange):
            return
        self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_CURRENT)
        super().setText("" if value is None else val2str(value))
        self._updateAppearance()

    @checked
    def new(self : Self) -> bool:
        return self.initial() is None

    @checked
    def changed(self : Self) -> bool:
        return self.initial() != self.value()

    @checked
    def deleted(self : Self) -> bool:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_DELETED)

    @checked
    def setDeleted(self : Self, deleted : bool) -> None:
        self.setData(deleted, Qt.ItemDataRole.UserRole + self._IDX_DELETED)
        self._updateAppearance()

    @checked
    def setEnabled(self : Self, enabled : bool) -> None:
        super().setEnabled(enabled)
        self._updateAppearance()

    @checked
    def setEditable(self : Self, editable : bool) -> None:
        super().setEditable(editable)
        self._updateAppearance()

    def _updateAppearance(self : Self) -> None:
        font = self.font()
        font.setItalic(not self.isEditable())
        font.setStrikeOut(self.deleted())
        self.setFont(font)
        bg_args = []
        if self.isEnabled():
            if self.deleted():
                bg_args.append(settings().get("theme/properties/deleted/color"))
            elif self.new():
                bg_args.append(settings().get("theme/properties/added/color"))
            elif self.changed():
                bg_args.append(settings().get("theme/properties/changed/color"))
            if not self.isEditable():
                bg_args.append(Qt.BrushStyle.Dense5Pattern)
        bg_brush = QBrush(*bg_args) if bg_args else None
        self.setData(bg_brush, Qt.ItemDataRole.BackgroundRole)


