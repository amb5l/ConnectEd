__all__ = ["AnchorPoint"]

from typing import Self

from . import APType, ElementAnchorPointsMixin

from .null_point import NullPoint
from .handle     import Handle


class AnchorPoint(NullPoint):
    # instance variables
    _name : str
    _type : "APType"
    _handle : Handle

    def __init__(
        self   : Self,
        name   : str,
        type   : "APType",
        parent : "ElementAnchorPointsMixin"
    ) -> None:
        super().__init__(parent)
        self._name   = name
        self._type   = type
        self._handle = Handle(self)
