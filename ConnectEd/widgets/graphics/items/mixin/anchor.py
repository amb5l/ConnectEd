from typing import Self

from PyQt6.QtCore import QRectF
from PyQt6.QtCore import QPointF

from ..anchor_point import AnchorPoint

from .grip import ItemGripMixin


class ItemAnchorPointsMixin(ItemGripMixin):
    # instance attributes
    _anchor_points : dict[str, "AnchorPoint"]

    def initAnchorPoints(self : Self) -> None:
        raise NotImplementedError("Subclass must implement this method")

    def getAnchorPoint(self : Self, name : str) -> "AnchorPoint":
        return self._anchor_points[name]

    def moveAnchorPointBy(self : Self, name : str, delta : QPointF) -> None:
        raise NotImplementedError("Subclass must implement this method")


class ItemRectAnchorPointsMixin(ItemAnchorPointsMixin):
    # class attributes
    _AP_RECT = {
        "Top Left"      : ( 0.0 , 0.0 ),
        "Top Center"    : ( 0.5 , 0.0 ),
        "Top Right"     : ( 1.0 , 0.0 ),
        "Center Left"   : ( 0.0 , 0.5 ),
        "Center"        : ( 0.5 , 0.5 ),
        "Center Right"  : ( 1.0 , 0.5 ),
        "Bottom Left"   : ( 0.0 , 1.0 ),
        "Bottom Center" : ( 0.5 , 1.0 ),
        "Bottom Right"  : ( 1.0 , 1.0 )
    }
    _AP_RESIZE = { k : k != "Center" for k in _AP_RECT.keys() }

    def initAnchorPoints(self : Self) -> None:
        self._anchor_points = {}
        for name, _ in self._AP_RECT.items():
            resize = name in self._AP_RESIZE
            anchor_point = AnchorPoint(name=name, resize=resize, parent=self)
            self._anchor_points[name] = anchor_point

    def anchorPointRect(self : Self) -> QRectF:
        raise NotImplementedError("Subclass must implement this method")

    def updateAnchorPoints(self : Self) -> None:
        if not hasattr(self, "_anchor_points"):
            return
        rect = self.anchorPointRect()
        x0 = rect.topLeft().x()
        y0 = rect.topLeft().y()
        w = rect.width()
        h = rect.height()
        for name, (x, y) in self._AP_RECT.items():
            self._anchor_points[name].setPos(QPointF(x0 + (x * w), y0 + (y * h)))
