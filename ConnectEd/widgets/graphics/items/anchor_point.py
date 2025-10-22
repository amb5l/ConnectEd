from typing import Self

from PyQt6.QtCore import QPointF

from .null_point import NullPoint
from .handle     import Grip, MoveGrip, ResizeGrip

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .mixin.anchor import ItemAnchorPointsMixin


class AnchorPoint(NullPoint):
    # instance attributes
    _name : str
    _grip : Grip

    def __init__(
        self   : Self,
        name   : str,
        pos    : QPointF = QPointF(),
        resize : bool = False,
        parent : "ItemAnchorPointsMixin" = None
    ) -> None:
        super().__init__(parent)
        self._name = name
        self.setPos(pos)
        grip_class = ResizeGrip if resize else MoveGrip
        self._grip = grip_class(self)

    def name(self : Self) -> str:
        return self._name

    def setName(self : Self, value : str) -> None:
        self._name = value
