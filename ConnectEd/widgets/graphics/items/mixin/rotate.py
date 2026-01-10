from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from ...property   import PropertySpec
from ...properties import PropertiesMixin


class ItemRotateMixin:
    # class attributes
    _PROPERTY_SPECS_ROTATE = {
        "Rotate" : PropertySpec(
            kind   = "float",
            valid  = lambda self: self.rotation() != 0,
            getter = lambda self: self.rotation(),
            setter = lambda self, value: self.setRotation(value)
        )
    }

    def initRotate(self : Self | QGraphicsItem) -> None:
        pass

    def onPositionChange(
        self : Self | QGraphicsItem | PropertiesMixin,
        _pos : QPointF | None = None
    ) -> None:
        if hasattr(self, "properties"):
            if "X" in self.properties:
                self.properties["X"].changed.emit(self.pos().x())
            if "Y" in self.properties:
                self.properties["Y"].changed.emit(self.pos().y())

    def onRotationChange(self : Self, angle : float) -> None:
        # propagate change to children for rotation compensation
        for child in self.childItems():
            if hasattr(child, "onSceneRotationChange"):
                child.onSceneRotationChange()
        # signal property value change
        if hasattr(self, "properties") and "Rotate" in self.properties:
            self.properties["Rotate"].changed.emit(self.rotation())

    def rotateCW(self : Self | QGraphicsItem) -> None:
        self.setRotation((self.rotation() + 90.0) % 360.0)

    def rotateCCW(self : Self | QGraphicsItem) -> None:
        self.setRotation((self.rotation() - 90.0) % 360.0)

    def parentSceneRotation(self : Self | QGraphicsItem) -> float:
        """Returns total effective rotation angle (degrees) of the parent."""
        angle = 0.0
        item = self.parentItem()
        while item is not None:
            angle += item.rotation()
            item = item.parentItem()
        return angle % 360.0

    def sceneRotation(self : Self | QGraphicsItem) -> float:
        """Returns total effective rotation angle (degrees) of the item."""
        return (self.parentSceneRotation() + self.rotation()) % 360.0
