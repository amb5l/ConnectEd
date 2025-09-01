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
        super().moveBy(offset.x(), offset.y())

    def setPosX(self : Self, value : float) -> None:
        pos = self.pos()
        pos.setX(value)
        self.setPos(pos)

    def setPosY(self : Self, value : float) -> None:
        pos = self.pos()
        pos.setY(value)
        self.setPos(pos)
