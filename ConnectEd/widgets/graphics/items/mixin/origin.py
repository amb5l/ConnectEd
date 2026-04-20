from typing      import Self
from dataclasses import replace

from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QTransform

from .....core.check import checked
from .....core.types import DataKind, HandleId

from ...properties import InherentProperty, PropertiesMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..handle import HandleItem
    from .handle  import ItemHandlesMixin


class ItemOriginMixin:
    # class attributes
    _ORIGIN : HandleId
    _PROPERTIES_ORIGIN = InherentProperty(
        kind   = None,
        worthy = lambda self: self.origin() is not None,
        getter = lambda self: self.origin(),
        setter = lambda self, value: self.setOrigin(value)
    )
    _PROPERTIES_RECT_ORIGIN = {
        "Origin" : replace(_PROPERTIES_ORIGIN, kind=DataKind.RECT_HANDLE)
    }
    _PROPERTIES_LINE_ORIGIN = {
        "Origin" : replace(_PROPERTIES_ORIGIN, kind=DataKind.LINE_HANDLE)
    }
    _PROPERTIES_BLOCK_PIN_ORIGIN = {
        "Origin" : replace(_PROPERTIES_ORIGIN, kind=DataKind.BLOCK_PIN_HANDLE)
    }
    _PROPERTIES_SYMBOL_PIN_ORIGIN = {
        "Origin" : replace(_PROPERTIES_ORIGIN, kind=DataKind.SYMBOL_PIN_HANDLE)
    }

    # instance attributes
    _origin  : HandleId                 # id of origin handle
    _handles : dict[str, "HandleItem"]

    def initOrigin(self : Self) -> None:
        from .handle import ItemHandlesMixin
        if not isinstance(self, ItemHandlesMixin):
            raise TypeError("ItemOriginMixin requires ItemHandlesMixin")
        if not hasattr(self, "_ORIGIN"):
            raise ValueError("ItemOriginMixin requires _ORIGIN")
        self.setOrigin(self._ORIGIN)

    @checked
    def origin(self : Self) -> HandleId:
        return self._origin

    @checked
    def setOrigin(
        self : Self | QGraphicsItem | PropertiesMixin,
        id   : HandleId
    ) -> None:
        """Set origin handle and update transform origin accordingly."""
        # record origin name
        self._origin = id
        # update origin
        self.updateOrigin()
        # broadcast change
        self.signalPropertyChanges("Origin")

    def getOriginHandle(self : "Self | ItemHandlesMixin") -> "HandleItem":
        return self.getHandle(self._origin)

    def updateOrigin(self : "Self | QGraphicsItem | ItemHandlesMixin") -> None:
        """Set transform origin to origin handle position, applying any mirror."""
        from .mirror import ItemMirrorMixin
        if not hasattr(self, "_handles") \
        or not hasattr(self, "_origin") \
        or self._origin is None:
            return  # initialising or has no named origin handle
        # get origin handle position
        origin_pos = self._handles[self._origin].pos()
        # set transform origin = origin handle position (rotation pivot)
        self.setTransformOriginPoint(origin_pos)
        # mirror scales (reflect around origin handle in local coords)
        sx = -1.0 if isinstance(self, ItemMirrorMixin) and self.mirrorH() else 1.0
        sy = -1.0 if isinstance(self, ItemMirrorMixin) and self.mirrorV() else 1.0
        # T(p) = (sx*(p - O).x, sy*(p - O).y) => origin handle lands at Qt item pos
        transform = QTransform()
        transform.scale(sx, sy)
        transform.translate(-origin_pos.x(), -origin_pos.y())
        self.setTransform(transform)
        # update grip appearance
        for handle in self._handles.values():
            handle.grip().onPathChange()
