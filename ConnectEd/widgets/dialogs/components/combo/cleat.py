from typing          import Self
from enum            import Enum

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QComboBox, QWidget

from .....core.check import checked
from .....core.types import HandleId, NoChange, NO_CHANGE
from .....core.utils import val2str

from ....graphics.items.mixin.handle import ItemHandlesMixin


class CleatComboBox(QComboBox):
    _initial : HandleId

    @checked
    def __init__(
        self   : Self,
        item   : ItemHandlesMixin,
        cleat  : HandleId,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._initial = cleat
        handle_id_type = item.handleIdType()
        if issubclass(handle_id_type, Enum):
            for member in handle_id_type:
                self.addItem(val2str(member), member)
                if member == cleat:
                    self.setCurrentIndex(self.count() - 1)

    @checked
    def value(self : Self) -> HandleId | NoChange:
        r = self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)
        return r if r != self._initial else NO_CHANGE
