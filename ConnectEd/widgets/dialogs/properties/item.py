from typing import Self, Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QStandardItem

from ....app import logger, settings

from ....core.check import checked
from ....core.types import NoChange, NO_CHANGE, DataKind
from ....core.utils import val2str, trace

from ...graphics.properties import PropertiesMixin


class PropertiesItem(QStandardItem):
    _IDX_OWNER   = 0
    _IDX_KIND    = 1
    _IDX_INITIAL = 2
    _IDX_CURRENT = 3
    _IDX_DEFAULT = 4
    _IDX_DELETED = 5

    @checked
    def __init__(
        self     : Self,
        owner    : PropertiesMixin,
        kind     : DataKind,
        value    : Any | None,         # None if existing
        default  : Any | None = None,  # None if default not applicable
        new      : bool = False,
        editable : bool = True,
        enabled  : bool = True
    ) -> None:
        super().__init__()
        self.setKind(kind)
        self.setInitial(None if new else value)
        self.setDefault(default)
        self.setDeleted(False)
        self.setEnabled(enabled)
        self.setEditable(editable)
        self.setValue(value)

    def setText(self : Self, text : str) -> None:
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
    def owner(self : Self) -> PropertiesMixin:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_OWNER)

    @checked
    def setOwner(self : Self, owner : PropertiesMixin) -> None:
        self.setData(owner, Qt.ItemDataRole.UserRole + self._IDX_OWNER)

    @checked
    def kind(self : Self) -> DataKind:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_KIND)

    @checked
    def setKind(self : Self, kind : DataKind | NoChange) -> None:
        if kind is NO_CHANGE:
            return
        self.setData(kind, Qt.ItemDataRole.UserRole + self._IDX_KIND)

    @checked
    def types(self : Self) -> tuple[type, ...]:
        return self.kind().types()

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
    def value(self : Self) -> Any | None:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_CURRENT)

    @checked
    def setValue(self : Self, value : Any | None | NoChange) -> None:
        if value is NO_CHANGE:
            return
        if not isinstance(value, self.types()) and value is not None:
            logger().error(f"Value {value} has invalid type: {type(value)}")
        else:
            self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_CURRENT)
            super().setText("" if value is None else val2str(value))
            self._updateAppearance()

    @checked
    def default(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_DEFAULT)

    @checked
    def setDefault(self : Self, value : Any) -> None:
        self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_DEFAULT)

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
    def setDeleted(self : Self, deleted: bool) -> None:
        self.setData(deleted, Qt.ItemDataRole.UserRole + self._IDX_DELETED)
        self._updateAppearance()

    def _updateAppearance(self : Self) -> None:
        font = self.font()
        font.setBold(self.changed())
        font.setStrikeOut(self.deleted())
        self.setFont(font)
        if self.value() is None:
            self.setData(None, Qt.ItemDataRole.BackgroundRole)
        elif self.deleted():
            self.setBackground(settings().get("theme/properties/deleted/color"))
        elif self.new():
            self.setBackground(settings().get("theme/properties/added/color"))
        elif self.changed():
            self.setBackground(settings().get("theme/properties/changed/color"))
        else:
            self.setData(None, Qt.ItemDataRole.BackgroundRole)
