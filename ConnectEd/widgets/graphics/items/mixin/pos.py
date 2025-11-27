from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from ...property import PropertySpec

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..mixin import ItemMixin


class ItemPosMixin:
    _PROPERTY_SPECS_POS = {
        "Position X" : PropertySpec(
            kind   = "float",
            getter = lambda self: self.pos().x(),
            setter = lambda self, value: self.setPosX(value)
        ),
        "Position Y" : PropertySpec(
            kind   = "float",
            getter = lambda self: self.pos().y(),
            setter = lambda self, value: self.setPosY(value)
        )
    }

    def moveBy(self : "Self | ItemMixin | QGraphicsItem", offset : QPointF) -> None:
        a = self.parentSceneRotation()
        match a:
            case 0   : super().moveBy(offset.x(), offset.y())
            case 90  : super().moveBy(offset.y(), -offset.x())
            case 180 : super().moveBy(-offset.x(), -offset.y())
            case 270 : super().moveBy(-offset.y(), offset.x())
            case _   :
                transform = QTransform().rotate(-a)
                rotated_offset = transform.map(offset)
                super().moveBy(rotated_offset.x(), rotated_offset.y())

    def setPos(self : "Self | ItemMixin | QGraphicsItem", pos : QPointF) -> None:
        """
        Set position, compensating for item's own rotation.
        When an item is rotated, position changes must be inverted accordingly.
        Supports 0/90/180/270 degree rotation angles only.
        """
        x = pos.x()
        y = pos.y()
        r = self.parentSceneRotation()
        match r:
            case 0   : pass
            case 90  : pos = QPointF(y, -x)
            case 180 : pos = QPointF(-x, -y)
            case 270 : pos = QPointF(-y, x)
            case _   : raise ValueError(f"Invalid rotation: {r}")
        super().setPos(pos)

    def setPosX(self : "Self | ItemMixin | QGraphicsItem", value : float) -> None:
        pos = self.pos()
        pos.setX(value)
        self.setPos(pos)

    def setPosY(self : "Self | ItemMixin | QGraphicsItem", value : float) -> None:
        pos = self.pos()
        pos.setY(value)
        self.setPos(pos)

    def parentSceneRotation(self: Self | QGraphicsItem) -> float:
            """
            Returns the effective rotation angle (degrees) of the parent
            w.r.t. the scene by summing hierarchy.
            """
            angle = 0.0
            item = self.parentItem()
            while item is not None:
                angle += item.rotation()
                item = item.parentItem()
            return angle % 360.0
