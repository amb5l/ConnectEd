from typing import Self

from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QTransform

from ...property   import PropertySpec
from ...properties import PropertiesMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..handle import HandleItem
    from .handle  import ItemHandlesMixin


class ItemOriginMixin:
    # class attributes
    _ORIGIN_NAME : str
    _PROPERTY_SPECS_ORIGIN = {
        "Origin" : PropertySpec(
            valid  = lambda self: self.getOrigin() is not None,
            getter = lambda self: self.getOrigin(),
            setter = lambda self, value: self.setOrigin(value)
        )
    }

    # instance attributes
    _origin  : str                  # name of origin handle
    _handles : dict[str, "HandleItem"]

    def initOrigin(self : Self) -> None:
        from .handle import ItemHandlesMixin
        if not isinstance(self, ItemHandlesMixin):
            raise TypeError("ItemOriginMixin requires ItemHandlesMixin")
        if not hasattr(self, "_ORIGIN_NAME"):
            raise ValueError("ItemOriginMixin requires _ORIGIN_NAME")
        self.setOrigin(self._ORIGIN_NAME)

    def getOrigin(self : Self) -> str:
        return self._origin

    def setOrigin(
        self   : Self | QGraphicsItem | PropertiesMixin,
        origin : str
    ) -> None:
        """Set origin handle and update transform origin accordingly."""
        # record origin name
        self._origin = origin
        # update origin
        self.updateOrigin()
        # broadcast change
        self.updateProperties("Origin")

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
