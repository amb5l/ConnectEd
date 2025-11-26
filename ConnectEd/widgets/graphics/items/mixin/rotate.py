from typing import Self, override

from PyQt6.QtWidgets import QGraphicsItem

from ...property import PropertySpec


class ItemRotateMixin:
    """Mixin to support and propagate rotation changes."""
    _PROPERTY_SPECS_ROT = {
        "Rotation" : PropertySpec(
            kind   = "float",
            getter = lambda self: self.rotation(),
            setter = lambda self, value: self.setRotation(value)
        )
    }

    def onRotationChange(self : Self) -> None:
        from ..handle import Handle
        for child in self.childItems():
            if hasattr(child, "onRotationChange"):
                child.onRotationChange()
            elif isinstance(child, Handle):
                for grandchild in child.childItems():
                    if hasattr(grandchild, "onRotationChange"):
                        grandchild.onRotationChange()

    def setRotation(self : Self, angle : float) -> None:
        from ...properties import PropertiesMixin
        super().setRotation(angle)
        self.onRotationChange()
        if isinstance(self, PropertiesMixin) \
        and "Rotation" in self.properties:
            self.properties["Rotation"].changed.emit(self.rotation())

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
