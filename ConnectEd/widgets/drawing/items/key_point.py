__all__ = ["KeyPoint"]

from typing import Self

from . import KPType, ElementKeypointsMixin

from .null_point import NullPoint
from .grip       import Grip


class KeyPoint(NullPoint):
    # instance variables
    _name : str
    _type : "KPType"
    _grip : Grip

    def __init__(
        self   : Self,
        name   : str,
        type   : "KPType",
        parent : "ElementKeypointsMixin"
    ) -> None:
        super().__init__(parent)
        self._name   = name
        self._type   = type
        self._grip   = Grip(self)
