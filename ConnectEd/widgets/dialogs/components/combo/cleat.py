from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QComboBox, QWidget

from .....core.types import HandleId

from ....graphics.items.mixin.handle import ItemHandlesMixin


class CleatComboBox(QComboBox):
    def __init__(
        self   : Self,
        item   : ItemHandlesMixin,
        cleat  : HandleId,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        for id in item.handleIdType():
            self.addItem(id.name(), id)
            if id == cleat:
                self.setCurrentIndex(self.count() - 1)

    def getCleat(self : Self) -> HandleId:
        # return user data for current index
        return self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)
