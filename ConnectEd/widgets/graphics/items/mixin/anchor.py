from typing import Self

from PyQt6.QtCore import QRectF
from PyQt6.QtCore import QPointF

from ..anchor_point import AnchorPoint

from .. import APType


class ElementAnchorPointsMixin:
    # instance attributes
    _anchor_points : dict[str, "AnchorPoint"]

    def getAnchorPoint(self : Self, name : str) -> "AnchorPoint":
        return self._anchor_points[name]


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
    _AP_TYPES : dict[str, APType]

    # instance attributes
    _rect   : QRectF   # border rectangle, maintained by element

    def initAnchorPoints(self : Self) -> None:
        from ..anchor_point import AnchorPoint
        self._anchor_points = {}
        for ap_name, ap_type in self._AP_TYPES.items():
            self._anchor_points[ap_name] = AnchorPoint(
                name   = ap_name,
                type   = ap_type,
                parent = self
            )

    def updateKeypoints(self : Self) -> None:
        for name, (x, y) in self._ANCHOR_POINTS.items():
            self._anchor_points[name].setPos(QPointF(
                x * self._rect.width(),
                y * self._rect.height()
            ))

    def updateHandlesVisibility(self : Self) -> None:
        for ap in self._anchor_points.values():
            ap._handle.setVisible(self.isSelected())
