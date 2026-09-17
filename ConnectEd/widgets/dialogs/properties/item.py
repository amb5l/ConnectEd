from typing import Self, Any, TypeVar, Generic
from types  import NoneType

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QStandardItem

from ....app import logger

from ....core.check import checked
from ....core.types import NoChange, DataKind
from ....core.utils import val2str, trace

from ..components.table import TableItem

from .types import ExistingChange, NewChange


T = TypeVar("T")


class ChangeItem(QStandardItem, Generic[T]):
    _READ_ONLY = False
    _IDX_VALUE = 0

    def __init__(self : Self, value : T) -> None:
        super().__init__()
        self.setEditable(not self._READ_ONLY)
        self.setValue(value)

    def value(self : Self) -> T:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_VALUE)

    def setValue(self : Self, value : T) -> None:
        self.setText(str(value))
        self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_VALUE)


class ExistingChangeItem(ChangeItem[ExistingChange]):
    pass


class NewChangeItem(ChangeItem[NewChange]):
    pass


class ExistingPropertyChangeItem(ExistingChangeItem):
    pass


class NewPropertyChangeItem(NewChangeItem):
    _READ_ONLY = True


class ExistingPropertyTextChangeItem(ExistingChangeItem):
    pass


class NewPropertyTextChangeItem(NewChangeItem):
    pass


class PropertiesItem(TableItem):
    _IDX_KIND    = 4
    _IDX_DEFAULT = 5

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
        self.setKind(kind)
        self.setInitial(None if new else value)
        self.setDefault(default)
        self.setValue(value)

    def setText(self : Self, atext : str | None) -> None:
        raise NotImplementedError("PropertiesItem.setText() is not implemented")

    def clear(self : Self) -> None:
        super().setText("")

    @checked
    def setEnabled(self : Self, enabled : bool) -> None:
        super().setEnabled(enabled)
        if not enabled or self.value() is None:
            super().setText("")
        else:
            super().setText(val2str(self.value()))

    @checked
    def kind(self : Self) -> DataKind | None:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_KIND)

    @checked
    def setKind(self : Self, kind : DataKind | NoChange) -> None:
        if isinstance(kind, NoChange):
            return
        old_kind = self.kind()
        if kind == old_kind:
            return
        self.setData(kind, Qt.ItemDataRole.UserRole + self._IDX_KIND)

    @checked
    def types(self : Self) -> tuple[type, ...]:
        if (kind := self.kind()) is None:
            return ()
        return kind.types()

    @checked
    def setInitial(self : Self, value : Any) -> None:
        if not isinstance(value, self.types() + (NoneType,)):  # None is allowed
            logger().error(f"Initial value {value} has invalid type: {type(value)}")
            trace(indent=True, args=True)
        else:
            super().setInitial(value)

    @checked
    def setValue(self : Self, value : Any | None | NoChange) -> None:
        if isinstance(value, NoChange):
            return
        if not isinstance(value, self.types()) and value is not None:
            logger().error(f"Value {value} has invalid type: {type(value)}")
            return
        super().setValue(value)
        # special case: value of "Type" column => kind of "Value" column
        from . import _COLS
        if self.column() == _COLS.index("Type"):
            if (model := self.model()) is None:
                return
            if isinstance(value_item := model.item(self.row(), _COLS.index("Value")), PropertiesItem):
                if not isinstance(value, DataKind):
                    logger().error(f"Value {value} is not a DataKind")
                else:
                    value_item.setKind(value)

    @checked
    def default(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_DEFAULT)

    @checked
    def setDefault(self : Self, value : Any) -> None:
        self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_DEFAULT)
