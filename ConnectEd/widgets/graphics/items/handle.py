from typing import Self, Text

from PyQt6.QtCore import QPointF

from .null import NullItem
from .grip import GripItem, MoveGripItem, ResizeGripItem, TextGripItem

from .mixin.change import ItemChangeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .mixin.handle import ItemHandlesMixin


class HandleItem(ItemChangeMixin, NullItem):
    # instance attributes
    _name : str
    _grip : GripItem

    def __init__(
        self   : Self,
        name   : str,
        pos    : QPointF | None = None,
        kind   : str = "resize",
        parent : "ItemHandlesMixin" = None
    ) -> None:
        super().__init__(parent)
        self._name = name
        self.setPos(pos or QPointF())
        grip_class = TextGripItem   if kind == "text" else \
                     ResizeGripItem if kind == "resize" else \
                     MoveGripItem
        self._grip = grip_class(self)

    def name(self : Self) -> str:
        return self._name

    def setName(self : Self, value : str) -> None:
        self._name = value

    def onOriginChange(self : Self) -> None:
        self._grip.onOriginChange()

    def onSceneRotationChange(self : Self) -> None:
        for child in self.childItems():
            if hasattr(child, "onSceneRotationChange"):
                child.onSceneRotationChange()

    def grip(self : Self) -> GripItem:
        return self._grip
