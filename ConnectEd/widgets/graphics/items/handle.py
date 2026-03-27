from typing import Self

from PyQt6.QtCore import QPointF

from ....core.types import HandleId

from .null import NullItem
from .grip import GripItem, MoveGripItem, ResizeGripItem, PolylineGripItem, TextGripItem

from .mixin.change import ItemChangeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .mixin.handle import ItemHandlesMixin


class HandleItem(ItemChangeMixin, NullItem):
    # instance attributes
    _id   : HandleId
    _grip : GripItem

    def __init__(
        self   : Self,
        id     : HandleId,
        pos    : QPointF | None = None,
        kind   : str = "resize",
        parent : "ItemHandlesMixin" = None
    ) -> None:
        super().__init__(parent)
        self._id = id
        self.setPos(pos or QPointF())
        grip_class = TextGripItem     if kind == "text"     else \
                     PolylineGripItem if kind == "polyline" else \
                     ResizeGripItem   if kind == "resize"   else \
                     MoveGripItem
        self._grip = grip_class(self)

    def id(self : Self) -> HandleId:
        return self._id

    def setId(self : Self, id : HandleId) -> None:
        self._id = id

    def onOriginChange(self : Self) -> None:
        self._grip.onOriginChange()

    def onSceneRotationChange(self : Self) -> None:
        for child in self.childItems():
            if hasattr(child, "onSceneRotationChange"):
                child.onSceneRotationChange()

    def grip(self : Self) -> GripItem:
        return self._grip
