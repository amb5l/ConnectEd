from typing import Self

from PyQt6.QtCore import QPointF

from .null_point import NullPoint
from .grip       import APGrip, MoveGrip, ResizeGrip

from .mixin.rotate import ItemRotateMixin
from .mixin.change import ItemChangeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .mixin.handle import ItemHandlesMixin


class Handle(ItemRotateMixin, ItemChangeMixin, NullPoint):
    # instance attributes
    _name : str
    _grip : APGrip

    def __init__(
        self   : Self,
        name   : str,
        pos    : QPointF | None = None,
        resize : bool = False,
        parent : "ItemHandlesMixin" = None
    ) -> None:
        super().__init__(parent)
        self._name = name
        if pos is None:
            pos = QPointF()
        self.setPos(pos)
        grip_class = ResizeGrip if resize else MoveGrip
        self._grip = grip_class(self)

    def name(self : Self) -> str:
        return self._name

    def setName(self : Self, value : str) -> None:
        self._name = value

    def onOriginChange(self : Self) -> None:
        self._grip.onOriginChange()

    def grip(self : Self) -> APGrip:
        return self._grip
