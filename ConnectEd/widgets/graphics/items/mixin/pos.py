from typing import Self, override, overload

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QTransform

from ...property   import PropertySpec
from ...properties import PropertiesMixin

class ItemPosMixin:
    # class attributes
    _INHERENT_PROPERTIES_POS = {
        "X" : PropertySpec(
            type_name = "float",
            valid     = lambda self: self.pos() != QPointF(0, 0),
            getter    = lambda self: self.pos().x(),
            setter    = lambda self, value: self.setX(value)
        ),
        "Y" : PropertySpec(
            type_name = "float",
            valid     = lambda self: self.pos() != QPointF(0, 0),
            getter    = lambda self: self.pos().y(),
            setter    = lambda self, value: self.setY(value)
        )
    }

    def initPos(self : Self | QGraphicsItem) -> None:
        pass

    def onPositionChange(
        self : Self | QGraphicsItem | PropertiesMixin,
        _pos : QPointF | None = None
    ) -> None:
        self.updateProperties(["X", "Y"])

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
