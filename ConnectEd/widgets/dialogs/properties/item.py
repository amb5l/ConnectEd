from __future__ import annotations

from typing import Self, Any

from PyQt6.QtCore import Qt

from ....core.check import checked
from ....core.types import NoChange, DataKind
from ....core.utils import val2str

from ...table.item import TableItem


class PropertiesItem(TableItem):
    """Adds writethrough and checkbox presentation support."""

    _IDX_REF  = 3
    _IDX_ATTR = 4  # to be used in combination with reference for writethrough

    _updating_presentation : bool

    def __init__(
        self     : Self,
        value    : Any,
        ref      : object | None = None,
        attr     : str    | None = None,
        new      : bool = False,
        editable : bool = True,
        enabled  : bool = True
    ) -> None:
        self._updating_presentation = False
        super().__init__(value, new, editable, enabled)
        self.setRef(ref)
        self.setAttr(attr)

    def setText(self : Self, atext : str | None) -> None:
        raise NotImplementedError("PropertiesItem.setText() is not implemented")

    def setData(
        self  : Self,
        value : Any,
        role  : int = Qt.ItemDataRole.UserRole
    ) -> None:
        # handle checkbox presentation
        if role == Qt.ItemDataRole.CheckStateRole \
        and isinstance(self.value(), bool):
            if self._updating_presentation:
                super().setData(value, role)
                return
            if not self.isEditable() or not self.isEnabled():
                return
            super().setData(value, role)
            bool_val = value == Qt.CheckState.Checked
            if self.value() is not bool_val:
                self.setValue(bool_val)
            return
        # EditRole is a user commit. Other roles store data for the item.
        if role == Qt.ItemDataRole.EditRole:
            super().setData(value, role)
            self.setValue(value)
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
    def setValue(self : Self, value : Any | NoChange) -> None:
        if isinstance(value, NoChange):
            return
        super().setValue(value)
        self._updatePresentation()
        # write through
        if (ref := self.ref()) is not None \
        and (attr := self.attr()) is not None:
            setattr(ref, attr, value)

    def ref(self : Self) -> object | None:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_REF)

    @checked
    def setRef(self : Self, value : object | None) -> None:
        self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_REF)

    @checked
    def attr(self : Self) -> str | None:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_ATTR)

    @checked
    def setAttr(self : Self, value : str | None) -> None:
        self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_ATTR)

    def _updatePresentation(self : Self) -> None:
        self._updating_presentation = True
        try:
            value = self.value()
            if isinstance(value, bool):
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


class PropertiesValueItem(PropertiesItem):
    """Adds kind to support property values."""

    _IDX_KIND = 5

    @checked
    def __init__(
        self     : Self,
        kind     : DataKind,
        value    : Any,
        ref      : object | None = None,
        attr     : str    | None = None,
        new      : bool = False,
        editable : bool = True,
        enabled  : bool = True
    ) -> None:
        super().__init__(value, ref, attr, new, editable, enabled)
        self.setKind(kind)

    @checked
    def kind(self : Self) -> DataKind | None:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_KIND)

    @checked
    def setKind(self : Self, kind : DataKind | NoChange) -> None:
        if isinstance(kind, NoChange):
            return
        super().setData(kind, Qt.ItemDataRole.UserRole + self._IDX_KIND)

    @checked
    def types(self : Self) -> tuple[type, ...]:
        if (kind := self.kind()) is None:
            return ()
        return kind.types()


class PropertiesExpanderItem(TableItem):
    """View expander. True expanded, False collapsed, None absent."""

    @checked
    def __init__(
        self     : Self,
        expanded : bool | None
    ) -> None:
        super().__init__(expanded)
        self.setCheckable(False)
        super().setText("")

    def setText(self : Self, atext : str | None) -> None:
        raise NotImplementedError(
            "PropertiesExpanderItem.setText() is not implemented"
        )

    @checked
    def setValue(self : Self, value : bool | None | NoChange) -> None:
        if isinstance(value, NoChange):
            return
        self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_CURRENT)
        self.setInitial(value)
        super().setText("")
