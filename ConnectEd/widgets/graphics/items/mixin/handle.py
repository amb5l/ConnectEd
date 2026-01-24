from typing import Self

from PyQt6.QtCore import QPointF, QRectF

from ..handle import HandleItem

from .grip import ItemGripMixin


class ItemHandlesMixin(ItemGripMixin):
    @classmethod
    def getHandleNames(cls : type[Self]) -> list[str]:
        raise NotImplementedError("Subclass must implement this method")

    # instance attributes
    _handles          : dict[str, "HandleItem"]

    def initHandles(self : Self) -> None:
        raise NotImplementedError("Subclass must implement this method")

    def getHandle(self : Self, name : str) -> "HandleItem":
        return self._handles[name]

    def moveHandleBy(self : Self, name : str, delta : QPointF) -> None:
        raise NotImplementedError("Subclass must implement this method")


class ItemRectHandlesMixin(ItemHandlesMixin):
    # class attributes
    _RESIZE_KIND = "resize"
    _AP_RECT = {
        "Top Left"      : ( 0.0 , 0.0 ),
        "Top Center"    : ( 0.5 , 0.0 ),
        "Top Right"     : ( 1.0 , 0.0 ),
        "Middle Left"   : ( 0.0 , 0.5 ),
        "Middle Center" : ( 0.5 , 0.5 ),
        "Middle Right"  : ( 1.0 , 0.5 ),
        "Bottom Left"   : ( 0.0 , 1.0 ),
        "Bottom Center" : ( 0.5 , 1.0 ),
        "Bottom Right"  : ( 1.0 , 1.0 )
    }
    _AP_RESIZE = [ k for k in _AP_RECT.keys() if k != "Middle Center" ]

    @classmethod
    def getHandleNames(cls : type[Self]) -> list[str]:
        return list(cls._AP_RECT.keys())


    def initHandles(self : Self) -> None:
        self._handles = {}
        for name in self._AP_RECT.keys():
            kind = self._RESIZE_KIND if name in self._AP_RESIZE else "move"
            handle = HandleItem(name=name, kind=kind, parent=self)
            self._handles[name] = handle

    def handleRect(self : Self) -> QRectF:
        raise NotImplementedError("Subclass must implement this method")

    def updateHandlePositions(self : Self) -> None:
        if not hasattr(self, "_handles"):
            return
        rect = self.handleRect()
        x0 = rect.topLeft().x()
        y0 = rect.topLeft().y()
        w = rect.width()
        h = rect.height()
        for name, (x, y) in self._AP_RECT.items():
            self._handles[name].setPos(QPointF(x0 + (x * w), y0 + (y * h)))
        if self.getOrigin() is not None:
            self.updateOrigin()

    def updateHandlePaths(self : Self) -> None:
        for handle in self._handles.values():
            handle.grip().onPathChange()
