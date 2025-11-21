from typing import Self, Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QStandardItem, QStandardItemModel

from ....core.utils import val2str, str2val


class DialogItem(QStandardItem):
    IDX_BEFORE    = 0
    IDX_KIND = 1
    IDX_DEFAULT   = 2

    def __init__(
        self     : Self,
        before   : Any,
        after    : Any = "",
        kind     : str = "str",
        default  : Any | None = None,
        editable : bool = True
    ) -> None:
        super().__init__(val2str(after))
        self.setBefore(before)
        self.setValue(after)
        self.setKind(kind)
        self.setDefault(default)
        self.setEditable(editable)

    def setInit(self : Self, value : Any) -> None:
        self.setBefore(value)
        self.setValue(value)

    def setBefore(self : Self, value : Any) -> None:
        self.setData(value, Qt.ItemDataRole.UserRole + self.IDX_BEFORE)

    def getBefore(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self.IDX_BEFORE)

    def setValue(self : Self, value : Any) -> None:
        self.setText(val2str(value))

    def getValue(self : Self) -> Any:
        return str2val(self.text(), self.getKind())

    def changed(self : Self) -> bool:
        return self.getValue() != self.getBefore() and self.getBefore() is not None

    def setKind(self : Self, kind : str) -> None:
        self.setData(kind, Qt.ItemDataRole.UserRole + self.IDX_KIND)

    def getKind(self : Self) -> str:
        return self.data(Qt.ItemDataRole.UserRole + self.IDX_KIND)

    def setDefault(self : Self, default : Any) -> None:
        self.setData(default, Qt.ItemDataRole.UserRole + self.IDX_DEFAULT)

    def getDefault(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self.IDX_DEFAULT)


class DialogModel(QStandardItemModel):
    pass
