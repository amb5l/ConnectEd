from typing import Self

from PyQt6.QtCore import QPointF

from ...properties import PropertySpec


class ElementPosMixin:
    _PROPERTY_SPECS_POS = {
        "Position X" : PropertySpec(
            type_name   = "float",
            getter      = lambda self: self.pos().x(),
            setter      = lambda self, value: self.setPosX(value)
        ),
        "Position Y" : PropertySpec(
            type_name   = "float",
            getter      = lambda self: self.pos().y(),
            setter      = lambda self, value: self.setPosY(value)
        )
    }

    def moveBy(self : Self, offset : QPointF) -> None:
        x = offset.x()
        y = offset.y()
        r = self.parentSceneRotation()
        match r:
            case 0   : super().moveBy(x, y)
            case 90  : super().moveBy(y, -x)
            case 180 : super().moveBy(-x, -y)
            case 270 : super().moveBy(-y, x)
            case _   : raise ValueError(f"Invalid rotation: {r}")

    def setPos(self : Self, pos : QPointF) -> None:
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

    def setPosX(self : Self, value : float) -> None:
        pos = self.pos()
        pos.setX(value)
        self.setPos(pos)

    def setPosY(self : Self, value : float) -> None:
        pos = self.pos()
        pos.setY(value)
        self.setPos(pos)
