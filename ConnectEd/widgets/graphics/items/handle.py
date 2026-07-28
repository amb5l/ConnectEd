from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from ....core.check import checked
from ....core.types import HandleId

from .role import ChromeItem

from .null import NullItem
from .grip import GripItem, MoveGripItem

from .protocols import OnSceneOrientationChangedProtocol

from .mixin.transform import ItemTransformMixin
from .mixin.change    import ItemChangeMixin


class HandleItem(ChromeItem, ItemChangeMixin, NullItem):
    # instance attributes
    _id   : HandleId
    _grip : GripItem

    @checked
    def __init__(
        self     : Self,
        id       : HandleId,
        pos      : QPointF | None = None,
        grip_cls : type[GripItem] = MoveGripItem,
        parent   : QGraphicsItem | None = None
    ) -> None:
        from .mixin.handle import ItemHandlesMixin
        if not isinstance(parent, ItemHandlesMixin): raise TypeError("Bad parent")
        super().__init__(parent)
        self._id = id
        self.setPos(pos or QPointF())
        self._grip = grip_cls(self)

    def id(self : Self) -> HandleId:
        return self._id

    @checked
    def setId(self : Self, id : HandleId) -> None:
        self._id = id

    def onSceneOrientationChanged(self : Self) -> None:
        for child in self.childItems():
            if isinstance(child, OnSceneOrientationChangedProtocol):
                child.onSceneOrientationChanged()

    def isOrigin(self : Self) -> bool:
        if isinstance(parent := self.parentItem(), ItemTransformMixin):
            return parent.hasOrigin() and parent.origin() == self.id()
        return False

    def grip(self : Self) -> GripItem:
        return self._grip
