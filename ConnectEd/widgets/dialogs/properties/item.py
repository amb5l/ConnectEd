from typing import Self, Any
from types  import NoneType

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QStandardItem, QBrush

from ....app import logger, settings

from ....core.check import checked
from ....core.types import NoChange, DataKind
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
        self.setDeleted(False)
        self.setKind(kind)
        self.setInitial(None if new else value)
        self.setDefault(default)
        self.setEnabled(enabled)
        self.setEditable(editable)
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
    def owner(self : Self) -> PropertiesMixin:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_OWNER)

    @checked
    def setOwner(self : Self, owner : PropertiesMixin) -> None:
        self.setData(owner, Qt.ItemDataRole.UserRole + self._IDX_OWNER)

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
        if kind != old_kind:
            # kind is being changed: applies only to custom properties
            old_value = self.value()
            new_value = None
            try:
                match kind:
                    case DataKind.STR | DataKind.TEXT:
                        new_value = str(old_value)
                    case DataKind.INT:
                        new_value = int(old_value)  # pyright: ignore[reportArgumentType]
                    case DataKind.FLOAT:
                        new_value = float(old_value)  # pyright: ignore[reportArgumentType]
                    case DataKind.BOOL:
                        new_value = bool(old_value)
                    case _:
                        logger().error(f"Invalid kind: {kind}")
            except ValueError:
                pass
            self.setValue(new_value)

    @checked
    def types(self : Self) -> tuple[type, ...]:
        if (kind := self.kind()) is None:
            return ()
        return kind.types()

    @checked
    def initial(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_INITIAL)

    @checked
    def setInitial(self : Self, value : Any) -> None:
        if not isinstance(value, self.types() + (NoneType,)):  # None is allowed
            logger().error(f"Initial value {value} has invalid type: {type(value)}")
            trace(indent=True, args=True)
        else:
            self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_INITIAL)

    @checked
    def value(self : Self) -> Any | None:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_CURRENT)

    @checked
    def setValue(self : Self, value : Any | None | NoChange) -> None:
        if isinstance(value, NoChange):
            return
        if not isinstance(value, self.types()) and value is not None:
            logger().error(f"Value {value} has invalid type: {type(value)}")
            return
        self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_CURRENT)
        super().setText("" if value is None else val2str(value))
        self._updateAppearance()
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
