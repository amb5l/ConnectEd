from typing import Self, override, overload

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QTransform

from ...property   import PropertySpec
from ...properties import PropertiesMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .handle import ItemHandlesMixin


class ItemPosRotMixin:
    """
    Manages origin, propagates rotation changes to children.
    """

    # class attributes
    _ORIGIN_NAME : str | None = None
    _PROPERTY_SPECS_POS_ROT = {
        "Origin" : PropertySpec(
            valid  = lambda self: self.getOrigin() is not None,
            getter = lambda self: self.getOrigin(),
            setter = lambda self, value: self.setOrigin(value)
        ),
        "X" : PropertySpec(
            kind   = "float",
            valid  = lambda self: self.pos() != QPointF(0, 0),
            getter = lambda self: self.pos().x(),
            setter = lambda self, value: self.setX(value)
        ),
        "Y" : PropertySpec(
            kind   = "float",
            valid  = lambda self: self.pos() != QPointF(0, 0),
            getter = lambda self: self.pos().y(),
            setter = lambda self, value: self.setY(value)
        ),
        "Rot" : PropertySpec(
            kind   = "float",
            valid  = lambda self: self.rotation() != 0,
            getter = lambda self: self.rotation(),
            setter = lambda self, value: self.setRotation(value)
        )
    }

    # instance attributes
    _origin : str | None     # name of origin handle

    def initPosRot(self : Self | QGraphicsItem) -> None:
        if hasattr(self, "_ORIGIN_NAME"):
            self.setOrigin(self._ORIGIN_NAME)
        else:
            self._origin = None

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
        # propagate change to enable rotation compensation
        from ..property_text import PropertyTextMixin
        if not isinstance(self, PropertyTextMixin):
            for child in self.childItems():
                if hasattr(child, "onSceneRotationChange"):
                    child.onSceneRotationChange()
        # signal property value change
        if hasattr(self, "properties") and "Rot" in self.properties:
            self.properties["Rot"].changed.emit(self.rotation())

    def getOrigin(self : Self | QGraphicsItem) -> str:
        return self._origin

    def setOrigin(
        self   : Self | QGraphicsItem | PropertiesMixin,
        origin : str
    ) -> None:
        """Set origin handle and update transform origin accordingly."""
        # record origin name
        self._origin = origin
        # update origin
        self.updateOrigin()
        # signal property value change
        if hasattr(self, "properties"):
            self.properties["Origin"].changed.emit(origin)

    def updateOrigin(self : "Self | QGraphicsItem | ItemHandlesMixin") -> None:
        """Set transform origin to origin handle position."""
        if not hasattr(self, "_handles") \
        or not hasattr(self, "_origin") \
        or self._origin is None:
            return  # initialising or has no named origin handle
        # get origin handle position
        origin_pos = self._handles[self._origin].pos()
        # set transform origin = origin handle position
        self.setTransformOriginPoint(origin_pos)
        # translate to position origin handle at Qt item position
        self.setTransform(QTransform().translate(
            -origin_pos.x(),
            -origin_pos.y()
        ))
        # update grip appearance
        for h in self._handles.values():
            h.onOriginChange()

    @overload
    def moveBy(self : Self | QGraphicsItem, dx : float, dy : float) -> None:
        ...

    @overload
    def moveBy(self : Self | QGraphicsItem, d : QPointF) -> None:
        ...

    @override
    def moveBy(
        self : Self | QGraphicsItem,
        dx_d : float | QPointF,
        dy   : float | None = None
    ) -> None:
        """Move item by scene offset, accounting for parent scene rotation."""
        dx = dx_d.x() if isinstance(dx_d, QPointF) else dx_d
        dy = dx_d.y() if isinstance(dx_d, QPointF) else dy
        a = self.parentSceneRotation()
        match a:
            case 0   : QGraphicsItem.moveBy(self,  dx,  dy)
            case 90  : QGraphicsItem.moveBy(self,  dy, -dx)
            case 180 : QGraphicsItem.moveBy(self, -dx, -dy)
            case 270 : QGraphicsItem.moveBy(self, -dy,  dx)
            case _   :
                transform = QTransform().rotate(-a)
                rotated_offset = transform.map(QPointF(dx, dy))
                QGraphicsItem.moveBy(self, rotated_offset.x(), rotated_offset.y())

    def rotateCW(self : Self | QGraphicsItem) -> None:
        self.setRotation((self.rotation() + 90) % 360)

    def rotateCCW(self : Self | QGraphicsItem) -> None:
        self.setRotation((self.rotation() - 90) % 360)

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
