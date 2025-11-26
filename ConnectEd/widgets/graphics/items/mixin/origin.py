from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QTransform

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
        return self._pos

    def setPos(self : Self, pos : QPointF) -> None:
        self._pos = pos
        origin_offset = self._origin.pos()
        transform = QTransform().rotate(QGraphicsItem.rotation(self))
        rotated_offset = transform.map(origin_offset)
        super().setPos(pos - rotated_offset)

    def getOriginScenePos(self : Self) -> QPointF:
        return self._origin.scenePos() if hasattr(self, "_origin") else self.scenePos()

    def getOrigin(self : Self) -> str:
        return self._origin.name() if hasattr(self, "_origin") else ""

    def setOrigin(self : Self, name : str) -> None:
        self._origin = self._handles[name]
        for h in self._handles.values():
            h.onOriginChange()
        self.updateOrigin()

    def updateOrigin(self : Self) -> None:
        """Reposition following possible movement of origin handle."""
        if not hasattr(self, "_origin"):
            return
        self.setPos(self._pos)
