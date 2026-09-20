from __future__ import annotations

from typing import Self, Any
from types  import NoneType

from PyQt6.QtCore import Qt

from ....app import logger

from ....core.check import checked
from ....core.types import NoChange, DataKind
from ....core.utils import val2str, trace

from ..components.table import TableItem


class PropertiesItem(TableItem):
    _IDX_KIND    = 4
    _IDX_DEFAULT = 5

    _updating_presentation : bool

    @checked
    def __init__(
        self     : Self,
        kind     : DataKind,
        value    : Any | None,         # None if existing
        default  : Any | None = None,  # None if default not applicable
        new      : bool = False,
        editable : bool = True,
        enabled  : bool = True
    ) -> None:
        super().__init__(new=new, editable=editable, enabled=enabled)
        self._updating_presentation = False
        self.setKind(kind)
        self.setInitial(None if new else value)
        self.setDefault(default)
        self.setValue(value)

    def setText(self : Self, atext : str | None) -> None:
        raise NotImplementedError("PropertiesItem.setText() is not implemented")

    def setData(
        self  : Self,
        value : Any,
        role  : int = Qt.ItemDataRole.UserRole
    ) -> None:
        if role == Qt.ItemDataRole.CheckStateRole \
        and self.kind() is DataKind.BOOL:
            if self._updating_presentation:
                super().setData(value, role)
                return
            if not self.isEditable() or not self.isEnabled():
                return
            super().setData(value, role)
            bool_val = value == Qt.CheckState.Checked
            if self.value() is not bool_val:
                super().setData(
                    bool_val,
                    Qt.ItemDataRole.UserRole + self._IDX_CURRENT
                )
                self._updateAppearance()
            return
        super().setData(value, role)

    @checked
    def setEnabled(self : Self, enabled : bool) -> None:
        super().setEnabled(enabled)
        self._updatePresentation()

    @checked
    def setEditable(self : Self, editable : bool) -> None:
        super().setEditable(editable)
        self._updatePresentation()

    @checked
    def setValue(self : Self, value : Any | None | NoChange) -> None:
        if isinstance(value, NoChange):
            return
        super().setValue(value)
        self._updatePresentation()

    @checked
    def kind(self : Self) -> DataKind | None:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_KIND)

    @checked
    def setKind(self : Self, kind : DataKind | NoChange) -> None:
        if isinstance(kind, NoChange):
            return
        super().setData(kind, Qt.ItemDataRole.UserRole + self._IDX_KIND)
        self._updatePresentation()

    @checked
    def types(self : Self) -> tuple[type, ...]:
        if (kind := self.kind()) is None:
            return ()
        return kind.types()

    @checked
    def default(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_DEFAULT)

    @checked
    def setDefault(self : Self, value : Any) -> None:
        self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_DEFAULT)

    def _updatePresentation(self : Self) -> None:
        self._updating_presentation = True
        try:
            value = self.value()
            if self.kind() is DataKind.BOOL and isinstance(value, bool):
                super().setText("")
                self.setCheckable(self.isEditable() and self.isEnabled())
                state = Qt.CheckState.Checked if value \
                    else Qt.CheckState.Unchecked
                super().setData(state, Qt.ItemDataRole.CheckStateRole)
                return
            self.setCheckable(False)
            super().setData(None, Qt.ItemDataRole.CheckStateRole)
            if not self.isEnabled() or value is None:
                super().setText("")
            else:
                super().setText(val2str(value))
        finally:
            self._updating_presentation = False
