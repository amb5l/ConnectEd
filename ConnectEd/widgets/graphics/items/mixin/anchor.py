from typing import Self

from PyQt6.QtCore import QRectF
from PyQt6.QtCore import QPointF

from ..anchor_point import APName, AnchorPoint


class ElementAnchorPointsMixin:
    # instance attributes
    _anchor_points : dict[APName, "AnchorPoint"]

    def getAnchorPoint(self : Self, name : APName) -> "AnchorPoint":
        return self._anchor_points[name]

    def moveAnchorPointBy(self : Self, name : APName, delta : QPointF) -> None:
        raise NotImplementedError("Subclass must implement this method")


class ElementRectAnchorPointsMixin(ElementAnchorPointsMixin):
    # class attributes
    _ANCHOR_POINTS = {
        APName.TopLeft      : ( 0.0 , 0.0 ),
        APName.TopCenter    : ( 0.5 , 0.0 ),
        APName.TopRight     : ( 1.0 , 0.0 ),
        APName.CenterLeft   : ( 0.0 , 0.5 ),
        APName.Center       : ( 0.5 , 0.5 ),
        APName.CenterRight  : ( 1.0 , 0.5 ),
        APName.BottomLeft   : ( 0.0 , 1.0 ),
        APName.BottomCenter : ( 0.5 , 1.0 ),
        APName.BottomRight  : ( 1.0 , 1.0 )
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
        for name, (x, y) in self._ANCHOR_POINTS.items():
            self._anchor_points[name].setPos(QPointF(
                x * self._rect.width(),
                y * self._rect.height()
            ))
