from typing import Self

from PyQt6.QtCore import QPointF

from ...property import PropertySpec

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..handle import Handle


class ItemOriginMixin:
    # class attributes
    _ORIGIN_NAME : str  # subclass must specify
    _PROPERTY_SPECS_ORIGIN = {
        "Origin" : PropertySpec(
            getter = lambda self: self.getOrigin(),
            setter = lambda self, value: self.setOrigin(value)
        )
    }

    # instance attributes
    _pos    : QPointF   # position of origin w.r.t. scene/parent
    _origin : "Handle"  # origin handle

    # external instance attributes
    _handles : dict[str, "Handle"]

    def initOrigin(self : Self) -> None:
        self._pos = super().pos()
        self._origin = self._handles[self._ORIGIN_NAME]
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

    def getOrigin(self : Self) -> str:
        if hasattr(self, "_origin"):
            return self._origin.name()
        else:
            return ""

    def setOrigin(self : Self, name : str) -> None:
        self._origin = self._handles[name]
        self.setPos(self.pos())
        for h in self._handles.values():
            h.onOriginChange()

    def updateOrigin(self : Self) -> None:
        """Reposition following possible movement of origin handle."""
        self.setPos(self._pos)
