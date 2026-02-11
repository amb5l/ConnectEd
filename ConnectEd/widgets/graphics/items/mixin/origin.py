from typing import Self

from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QTransform

from .....core.checks import checked
from .....core.types  import HandleId

from ...properties import InherentProperty, PropertiesMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..handle import HandleItem
    from .handle  import ItemHandlesMixin


class ItemOriginMixin:
    # class attributes
    _ORIGIN : HandleId
    _PROPERTIES_ORIGIN = {
        "Origin" : InherentProperty(
            kind   = "Str",
            valid  = lambda self: self.origin() is not None,
            getter = lambda self: self.origin(),
            setter = lambda self, value: self.setOrigin(value)
        )
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
        """Set transform origin to origin handle position."""
        if not hasattr(self, "_handles") \
        or not hasattr(self, "_origin") \
        or self._origin is None:
            return  # initialising or has no named origin handle
        # get origin handle position
        origin_pos = self._handles[self._origin].pos()
        # set transform origin = origin handle position
        self.setTransformOriginPoint(origin_pos)
        # translate to position origin handle at Qt item position
        self.setTransform(QTransform().translate(
            -origin_pos.x(),
            -origin_pos.y()
        ))
        # update grip appearance
        for handle in self._handles.values():
            handle.grip().onPathChange()
