from typing import Self

from PyQt6.QtCore import QPointF

from ...properties import PropertySpec

from ..anchor_point import AnchorPoint
from ..handle       import Origin


class ElementOriginMixin:
    # class attributes
    _ORIGIN : str  # subclass must specify
    _PROPERTY_SPECS_ORIGIN = {
        "Origin" : PropertySpec(
            type_name   = "str",
            getter      = lambda self: self.getOriginAPName(),
            setter      = lambda self, value: self.setOriginAPName(value),
            description = "Origin anchor point"
        )
    }

    # instance attributes
    _pos    : QPointF  # position of origin w.r.t. scene/parent
    _origin : Origin   # origin object

    # external instance attributes
    _anchor_points : dict[str, AnchorPoint]

    def initOrigin(self : Self) -> None:
        self._pos = super().pos()
        self._origin = Origin(self._anchor_points[self._ORIGIN])
        self.updateOrigin()

    def pos(self : Self) -> QPointF:
        return super().pos() + self._origin.parentItem().pos()

    def setPos(self : Self, pos : QPointF) -> None:
        self._pos = pos
        super().setPos(pos - self._origin.parentItem().pos())

    def getOriginScenePos(self : Self) -> QPointF:
        if hasattr(self, "_origin"):
            return self._origin.scenePos()
        else:
            return self.scenePos()

    def getOriginAP(self : Self) -> AnchorPoint:
        return self._origin.parentItem()

    def setOriginAP(self : Self, ap : AnchorPoint) -> None:
        self._origin.setParentItem(ap)
        self.setPos(self.pos())

    def getOriginAPName(self : Self) -> str:
        ap : AnchorPoint = self._origin.parentItem()
        return ap.name()

    def setOriginAPName(self : Self, name : str) -> None:
        self.setOriginAP(self._anchor_points[name])
        self.setPos(self.pos())

    def updateOrigin(self : Self) -> None:
        """Reposition following possible movement of origin anchor point."""
        self.setPos(self._pos)
