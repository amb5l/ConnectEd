from typing import Self

from PyQt6.QtCore import QRectF
from PyQt6.QtCore import QPointF

from ..anchor_point import AnchorPoint


class ElementAnchorPointsMixin:
    # instance attributes
    _anchor_points : dict[str, "AnchorPoint"]

    def getAnchorPoint(self : Self, name : str) -> "AnchorPoint":
        return self._anchor_points[name]

    def moveAnchorPointBy(self : Self, name : str, delta : QPointF) -> None:
        raise NotImplementedError("Subclass must implement this method")


class ElementRectAnchorPointsMixin(ElementAnchorPointsMixin):
    # class attributes
    _ANCHOR_POINTS = {
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
    _AP_RESIZE = { k : k != "Center" for k in _ANCHOR_POINTS.keys() }

    # external instance attributes
    _rect : QRectF  # border rectangle, maintained by element

    def initAnchorPoints(self : Self) -> None:
        self._anchor_points = {}
        for name, _ in self._ANCHOR_POINTS.items():
            resize = name in self._AP_RESIZE
            anchor_point = AnchorPoint(name=name, resize=resize, parent=self)
            self._anchor_points[name] = anchor_point

    def updateAnchorPoints(self : Self) -> None:
        if not hasattr(self, "_anchor_points"):
            return
        for name, (x, y) in self._ANCHOR_POINTS.items():
            self._anchor_points[name].setPos(QPointF(
                x * self._rect.width(),
                y * self._rect.height()
            ))
