from typing import Self
from enum   import Enum

from PyQt6.QtCore import QPointF

from .null_point import NullPoint
from .handle     import Grip, MoveGrip, ResizeGrip

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .mixin.anchor import ElementAnchorPointsMixin


class APName(Enum):
    TopLeft      = "Top Left"
    TopCenter    = "Top Center"
    TopRight     = "Top Right"
    CenterLeft   = "Center Left"
    Center       = "Center"
    CenterRight  = "Center Right"
    BottomLeft   = "Bottom Left"
    BottomCenter = "Bottom Center"
    BottomRight  = "Bottom Right"
    Origin       = "Origin"
    Name         = "Name"
    Node         = "Node"
    Undefined    = "Undefined"


class AnchorPoint(NullPoint):
    # instance attributes
    _name   : APName
    _grip   : Grip

    def __init__(
        self   : Self,
        name   : APName,
        pos    : QPointF = QPointF(),
        resize : bool = False,
        parent : "ElementAnchorPointsMixin" = None
    ) -> None:
        super().__init__(parent)
        self._name = name
        self.setPos(pos)
        grip_class = ResizeGrip if resize else MoveGrip
        self._grip = grip_class(self)

    def name(self : Self) -> APName:
        return self._name

    def setName(self : Self, value : APName) -> None:
        self._name = value
