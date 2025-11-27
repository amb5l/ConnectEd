from typing import Self

from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QGraphicsItem

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
    _origin_name   : str      # name of origin handle
    _origin_offset : QPointF  # offset of origin w.r.t. top left (Qt pos)

    # external instance attributes
    _handles : dict[str, "Handle"]

    def initOrigin(self : Self | QGraphicsItem) -> None:
        self._origin_offset = QPointF()
        self.setOrigin(self._ORIGIN_NAME)
        self.setPos(super().pos())

    def pos(self : Self | QGraphicsItem) -> QPointF:
        return super().pos() + self._origin_offset

    def setPos(self : Self | QGraphicsItem, pos : QPointF) -> None:
        super().setPos(pos - self._origin_offset)

    def scenePos(self : Self | QGraphicsItem) -> QPointF:
        return self.mapToScene(self._origin_offset)

    def getOrigin(self : Self | QGraphicsItem) -> str:
        return self._origin_name

    def setOrigin(self : Self | QGraphicsItem, name : str) -> None:
        pos = self.pos() if hasattr(self, "_origin_offset") else super().pos()
        self._origin_name = name
        for h in self._handles.values():
            h.onOriginChange()
        self.updateHandles()  # writes _origin_offset
        self.setPos(pos)
