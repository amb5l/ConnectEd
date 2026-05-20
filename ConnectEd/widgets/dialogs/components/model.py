from typing import Self, Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QStandardItem, QStandardItemModel

from ....core.check import checked
from ....core.utils import val2str, str2val


class BaseItem(QStandardItem):
    IDX_INITIAL   = 0
    IDX_TYPE_NAME = 1
    IDX_DEFAULT   = 2

    @checked
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

    @checked
    def setInitial(self : Self, value : Any) -> None:
        self.setData(value, Qt.ItemDataRole.UserRole + self.IDX_INITIAL)

    @checked
    def getBefore(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self.IDX_INITIAL)

    @checked
    def setValue(self : Self, value : Any) -> None:
        self.setText(val2str(value))

    @checked
    def getValue(self : Self) -> Any:
        return str2val(self.text(), self.getTypeName())

    @checked
    def changed(self : Self) -> bool:
        return self.getValue() != self.getBefore() and self.getBefore() is not None

    @checked
    def setTypeName(self : Self, kind : str) -> None:
        self.setData(kind, Qt.ItemDataRole.UserRole + self.IDX_TYPE_NAME)

    @checked
    def getTypeName(self : Self) -> str:
        return self.data(Qt.ItemDataRole.UserRole + self.IDX_TYPE_NAME)

    @checked
    def setDefault(self : Self, default : Any) -> None:
        self.setData(default, Qt.ItemDataRole.UserRole + self.IDX_DEFAULT)

    @checked
    def getDefault(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self.IDX_DEFAULT)


class BaseModel(QStandardItemModel):
    pass
