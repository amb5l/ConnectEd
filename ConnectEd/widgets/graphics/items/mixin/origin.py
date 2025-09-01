from typing import Self

from PyQt6.QtCore import QPointF

from ...properties import PropertySpec

from ..anchor_point import AnchorPoint


class ElementOriginMixin:
    # class attributes
    _PROPERTY_SPECS_ORIGIN = {
        "Origin" : PropertySpec(
            type_name   = "AnchorPoint",
            getter      = lambda self: self.getOrigin(),
            setter      = lambda self, value: self.setOrigin(value),
            description = "Origin anchor point"
        )
    }

    # instance attributes
    _pos    : QPointF        # position of origin w.r.t. scene/parent
    _origin : "AnchorPoint"  # origin anchor point

    def initOrigin(self : Self) -> None:
        self._pos = super().pos()
        self._origin = next(iter(self._anchor_points.values()))
        self._origin._handle.onOriginChange(True)
        self.updateOrigin()

    def pos(self : Self) -> QPointF:
        return super().pos() + self._origin.pos()

    def setPos(self : Self, pos : QPointF) -> None:
        self._pos = pos
        super().setPos(pos - self._origin.pos())

    def getOrigin(self : Self) -> str:
        return self._origin._name

    def setOrigin(self, name : str) -> None:
        self._origin._handle.onOriginChange(False)
        self._origin = self._anchor_points[name]
        self._origin._handle.onOriginChange(True)
        self.setPos(self.pos())

    def updateOrigin(self : Self) -> None:
        """Reposition following possible movement of origin anchor point."""
        self.setPos(self._pos)