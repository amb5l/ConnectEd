from typing import Self, override

from PyQt6.QtWidgets import QGraphicsItem

from .properties import ItemPropertySpec


class ItemRotateMixin:
    """Mixin to support and propagate rotation changes."""
    _PROPERTY_SPECS_ROT = {
        "Rotation" : ItemPropertySpec(
            type_name = "float",
            getter    = lambda self: self.rotation(),
            setter    = lambda self, value: self.setRotation(value)
        )
    }

    def onRotationChange(self : Self) -> None:
        for child in self.childItems():
            if hasattr(child, "onRotationChange"):
                child.onRotationChange()

    @override
    def setRotation(self : Self | QGraphicsItem, angle : float) -> None:
        """Override to call onRotationChange."""
        old = self.rotation()
        super().setRotation(angle)
        if old != angle:
            if hasattr(self, 'onRotationChange'):
                self.onRotationChange()

    def rotateCW(self : Self | QGraphicsItem) -> None:
        self.setRotation((self.rotation() + 90) % 360)

    def rotateCCW(self : Self | QGraphicsItem) -> None:
        self.setRotation((self.rotation() - 90) % 360)

    def sceneRotation(self: Self | QGraphicsItem) -> float:
        angle = 0.0
        item = self
        while item is not None:
            angle += item.rotation()
            item = item.parentItem()
        return angle % 360.0
