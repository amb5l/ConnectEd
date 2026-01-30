from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from ...properties import InherentProperty, PropertiesMixin


class ItemRotateMixin:
    # class attributes
    _PROPERTIES_ROTATE = {
        "Rotate" : InherentProperty(
            type_name = "float",
            valid     = lambda self: self.rotation() != 0,
            getter    = lambda self: self.rotation(),
            setter    = lambda self, value: self.setRotation(value)
        )
    }

    def initRotate(self : Self | QGraphicsItem) -> None:
        pass

    def onPositionChange(
        self : Self | QGraphicsItem | PropertiesMixin,
        _pos : QPointF | None = None
    ) -> None:
        self.signalPropertyChanges("Rotate")

    def onRotationChange(self : Self | PropertiesMixin, angle : float) -> None:
        # handle own rotation compensation
        if hasattr(self, "onSceneRotationChange"):
            self.onSceneRotationChange()
        # propagate to children
        for child in self.childItems():
            if hasattr(child, "onSceneRotationChange"):
                child.onSceneRotationChange()
        # broadcast change
        self.signalPropertyChanges("Rotate")

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
