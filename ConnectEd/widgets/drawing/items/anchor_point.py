__all__ = ["AnchorPoint"]

from typing import Self

from PyQt6.QtCore import QPointF

from . import APType, ElementAnchorPointsMixin

from .null_point import NullPoint
from .handle     import Handle


class AnchorPoint(NullPoint):
    # instance attributes
    _name : str
    _type : "APType"
    _handle : Handle

    def __init__(
        self   : Self,
        name   : str                        = "",
        type   : "APType"                   = APType.Static,
        pos    : QPointF                    = QPointF(),
        parent : "ElementAnchorPointsMixin" = None
    ) -> None:
        super().__init__(parent)
        self._name   = name
        self._type   = type
        self._handle = Handle(self)
