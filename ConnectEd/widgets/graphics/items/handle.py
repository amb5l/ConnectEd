from typing import Self

from PyQt6.QtCore import QPointF

from ....core.check import checked
from ....core.types import HandleId

from .null import NullItem
from .grip import GripItem, MoveGripItem

from .mixin.transform import ItemTransformMixin
from .mixin.change    import ItemChangeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .mixin.handle import ItemHandlesMixin


class HandleItem(ItemChangeMixin, NullItem):
    # instance attributes
    _id   : HandleId
    _grip : GripItem

    def __init__(
        self     : Self,
        id       : HandleId,
        pos      : QPointF | None = None,
        grip_cls : type[GripItem] = MoveGripItem,
        parent   : "ItemHandlesMixin" = None
    ) -> None:
        super().__init__(parent)
        self._id = id
        self.setPos(pos or QPointF())
        self._grip = grip_cls(self)

    def id(self : Self) -> HandleId:
        return self._id

    @checked
    def setId(self : Self, id : HandleId) -> None:
        self._id = id

    def onSceneRotationChange(self : Self) -> None:
        for child in self.childItems():
            if hasattr(child, "onSceneRotationChange"):
                child.onSceneRotationChange()

    def isOrigin(self : Self) -> bool:
        parent = self.parentItem()
        if isinstance(parent, ItemTransformMixin):
            return parent.origin() == self.id()
        return False

    def grip(self : Self) -> GripItem:
        return self._grip
