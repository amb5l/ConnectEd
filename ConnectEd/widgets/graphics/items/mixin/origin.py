from typing import Self

from PyQt6.QtCore import QPointF

from ...properties import PropertySpec

from ..anchor_point import APName, AnchorPoint
from ..handle       import Origin


class ElementOriginMixin:
    # class attributes
    _ORIGIN : APName  # subclass must specify
    _PROPERTY_SPECS_ORIGIN = {
        "Origin" : PropertySpec(
            type_name   = "AnchorPoint",
            getter      = lambda self: self.getOrigin(),
            setter      = lambda self, value: self.setOrigin(value),
            description = "Origin anchor point"
        )
    }

    # instance attributes
    _pos    : QPointF  # position of origin w.r.t. scene/parent
    _origin : Origin   # origin anchor point

    # external instance attributes
    _anchor_points : dict[APName, AnchorPoint]

    def initOrigin(self : Self) -> None:
        self._pos = super().pos()
        self._origin = Origin(self._anchor_points[self._ORIGIN])
        print(f"initOrigin : {self._origin}")
        self.updateOrigin()

    def pos(self : Self) -> QPointF:
        return super().pos() + self._origin.pos()

    def setPos(self : Self, pos : QPointF) -> None:
        self._pos = pos
        super().setPos(pos - self._origin.pos())

    def getOrigin(self : Self) -> APName:
        ap : AnchorPoint = self._origin.parentItem()
        return ap.name

    def setOrigin(self, ap : APName) -> None:
        self._origin.setParentItem(self._anchor_points[ap])
        self.setPos(self.pos())

    def updateOrigin(self : Self) -> None:
        """Reposition following possible movement of origin anchor point."""
        self.setPos(self._pos)
