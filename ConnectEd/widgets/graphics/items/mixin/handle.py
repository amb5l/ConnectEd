from typing import Self

from PyQt6.QtCore import QPointF, QRectF

from .....core.types import HandleId, RectHandleId

from ..handle import HandleItem

from .origin import ItemOriginMixin
from .grip   import ItemGripMixin


class ItemHandlesMixin(ItemGripMixin):
    def getHandle(self : Self, id : HandleId) -> "HandleItem":
        return self._handles[id]

    def moveHandleBy(self : Self, id : HandleId, d : QPointF) -> None:
        raise NotImplementedError("Subclass must implement this method")


class ItemRectHandlesMixin(ItemHandlesMixin):
    # instance attributes
    _handles : dict[RectHandleId, "HandleItem"]

    def initHandles(self : Self) -> None:
        self._handles = {}
        for id in RectHandleId:
            kind = "move" if id == RectHandleId.MIDDLE_CENTER else "resize"
            handle = HandleItem(id=id, kind=kind, parent=self)
            self._handles[id] = handle

    def handleRect(self : Self) -> QRectF:
        raise NotImplementedError("Subclass must implement this method")

    def updateHandlePositions(self : Self | ItemOriginMixin) -> None:
        if not hasattr(self, "_handles"):
            return
        rect = self.handleRect()
        x0 = rect.topLeft().x()
        y0 = rect.topLeft().y()
        w = rect.width()
        h = rect.height()
        for id in RectHandleId:
            name = id.value
            x = 1.0 if "Right" in name else 0.5 if "Center" in name else 0.0
            y = 1.0 if "Bottom" in name else 0.5 if "Middle" in name else 0.0
            self._handles[id].setPos(QPointF(x0 + (x * w), y0 + (y * h)))
        if self.origin() is not None:
            self.updateOrigin()

    def updateHandlePaths(self : Self) -> None:
        for handle in self._handles.values():
            handle.grip().onPathChange()
