from typing import Self, Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QStandardItem, QStandardItemModel

from ....core.utils import val2str, str2val


class BaseItem(QStandardItem):
    IDX_INITIAL   = 0
    IDX_TYPE_NAME = 1
    IDX_DEFAULT   = 2

    def __init__(
        self      : Self,
        initial   : Any,
        value     : Any = "",
        type_name : str = "str",
        default   : Any = None,
        editable  : bool = True,
        enabled   : bool = True
    ) -> None:
        super().__init__()
        self.setInitial(initial)
        self.setValue(value)
        self.setTypeName(type_name)
        self.setDefault(default)
        self.setEditable(editable)

    def setInitial(self : Self, value : Any) -> None:
        self.setData(value, Qt.ItemDataRole.UserRole + self.IDX_INITIAL)

    def getBefore(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self.IDX_INITIAL)

    def setValue(self : Self, value : Any) -> None:
        self.setText(val2str(value))

    def getValue(self : Self) -> Any:
        return str2val(self.text(), self.getTypeName())

    def changed(self : Self) -> bool:
        return self.getValue() != self.getBefore() and self.getBefore() is not None

    def setTypeName(self : Self, kind : str) -> None:
        self.setData(kind, Qt.ItemDataRole.UserRole + self.IDX_TYPE_NAME)

    def getTypeName(self : Self) -> str:
        return self.data(Qt.ItemDataRole.UserRole + self.IDX_TYPE_NAME)

    def setDefault(self : Self, default : Any) -> None:
        self.setData(default, Qt.ItemDataRole.UserRole + self.IDX_DEFAULT)

    def getDefault(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self.IDX_DEFAULT)


class BaseModel(QStandardItemModel):
    pass
