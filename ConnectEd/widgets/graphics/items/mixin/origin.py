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
        offset = getattr(self, "_origin_offset", QPointF())
        return super().pos() + offset

    def setPos(self : Self | QGraphicsItem, pos : QPointF) -> None:
        offset = getattr(self, "_origin_offset", QPointF())
        super().setPos(pos - offset)

    def scenePos(self : Self | QGraphicsItem) -> QPointF:
        return self.mapToScene(self._origin_offset)

    def getOrigin(self : Self | QGraphicsItem) -> str:
        return self._origin_name

    def setOrigin(self : Self | QGraphicsItem, name : str) -> None:
        """Set origin handle and update position."""
        pos = self.pos()
        self._origin_name = name
        self.updateOrigin()
        for h in self._handles.values():
            h.onOriginChange()
        self.setPos(pos)

    def updateOrigin(self : Self | QGraphicsItem) -> None:
        """Update origin offset and transform origin based on current handle position."""
        if hasattr(self, "_origin_name") and hasattr(self, "_handles"):
            self._origin_offset = self._handles[self._origin_name].pos()
            self.setTransformOriginPoint(self._origin_offset)
