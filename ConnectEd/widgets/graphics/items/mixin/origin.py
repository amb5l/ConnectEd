from typing import Self

from PyQt6.QtCore import QPointF

from ...properties import PropertySpec

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..anchor_point import AnchorPoint


class ItemOriginMixin:
    # class attributes
    _ORIGIN_NAME : str  # subclass must specify
    _PROPERTY_SPECS_ORIGIN = {
        "Origin" : PropertySpec(
            type_name   = "str",
            getter      = lambda self: self.getOriginAPName(),
            setter      = lambda self, value: self.setOriginAPName(value),
            description = "Origin anchor point"
        )
    }

    # instance attributes
    _pos    : QPointF        # position of origin w.r.t. scene/parent
    _origin : "AnchorPoint"  # origin anchor point

    # external instance attributes
    _anchor_points : dict[str, "AnchorPoint"]

    def initOrigin(self : Self) -> None:
        self._pos = super().pos()
        self._origin = self._anchor_points[self._ORIGIN_NAME]
        self.updateOrigin()

    def pos(self : Self) -> QPointF:
        return super().pos() + self._origin.pos()

    def setPos(self : Self, pos : QPointF) -> None:
        self._pos = pos
        super().setPos(pos - self._origin.pos())

    def getOriginScenePos(self : Self) -> QPointF:
        if hasattr(self, "_origin"):
            return self._origin.scenePos()
        else:
            return self.scenePos()

    def getOriginAP(self : Self) -> "AnchorPoint":
        return self._origin

    def setOriginAP(self : Self, ap : "AnchorPoint") -> None:
        self._origin = ap
        self.setPos(self.pos())
        for ap in self._anchor_points.values():
            ap.onOriginChange()

    def getOriginAPName(self : Self) -> str:
        if hasattr(self, "_origin"):
            return self._origin.name()
        else:
            return ""

    def setOriginAPName(self : Self, name : str) -> None:
        self.setOriginAP(self._anchor_points[name])

    def updateOrigin(self : Self) -> None:
        """Reposition following possible movement of origin anchor point."""
        self.setPos(self._pos)
