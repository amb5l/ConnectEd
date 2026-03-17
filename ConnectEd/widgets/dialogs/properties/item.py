from typing import Self, Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QStandardItem

from ....app import logger

from ....core.check import checked
from ....core.types import DataKind
from ....core.utils import val2str, trace

from ...graphics.properties import PropertiesMixin


class PropertiesItem(QStandardItem):
    _IDX_OWNER   = 0
    _IDX_KIND    = 1
    _IDX_TYPES   = 2
    _IDX_INITIAL = 3
    _IDX_CURRENT = 4
    _IDX_DEFAULT = 5

    @checked
    def __init__(
        self     : Self,
        owner    : PropertiesMixin,
        kind     : DataKind,
        value    : Any,           # None if existing
        default  : Any  = None,   # None if default not applicable
        new      : bool = False,
        editable : bool = True,
        enabled  : bool = True
    ) -> None:
        super().__init__()
        self.setKind(kind)
        self.setInitial(None if new else value)
        self.setValue(value)
        self.setDefault(default)
        self.setEnabled(enabled)
        self.setEditable(editable)

    @checked
    def setEnabled(self : Self, enabled : bool) -> None:
        super().setEnabled(enabled)
        self.setText(val2str(self.value()) if enabled else "")

    @checked
    def owner(self : Self) -> PropertiesMixin:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_OWNER)

    @checked
    def setOwner(self : Self, owner : PropertiesMixin) -> None:
        self.setData(owner, Qt.ItemDataRole.UserRole + self._IDX_OWNER)

    @checked
    def kind(self : Self) -> DataKind:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_KIND)

    @checked
    def setKind(self : Self, kind : DataKind) -> None:
        self.setData(kind, Qt.ItemDataRole.UserRole + self._IDX_KIND)
        self.setData(kind.types, Qt.ItemDataRole.UserRole + self._IDX_TYPES)

    @checked
    def types(self : Self) -> tuple[type, ...]:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_TYPES)

    @checked
    def initial(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_INITIAL)

    @checked
    def setInitial(self : Self, value : Any) -> None:
        if not isinstance(value, self.types() + (type(None),)):  # None is allowed
            logger().error(f"Initial value {value} has invalid type: {type(value)}")
            trace(indent=True, args=True)
        else:
            self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_INITIAL)

    @checked
    def value(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_CURRENT)

    @checked
    def setValue(self : Self, value : Any) -> None:
        if not isinstance(value, self.types()):
            logger().error(f"Value {value} has invalid type: {type(value)}")
        else:
            self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_CURRENT)
            self.setText(val2str(value))

    @checked
    def default(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_DEFAULT)

    @checked
    def setDefault(self : Self, value : Any) -> None:
        self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_DEFAULT)

    @checked
    def changed(self : Self) -> bool:
        return self.initial() != self.value()
