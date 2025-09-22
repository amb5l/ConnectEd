from typing import Self

from PyQt6.QtCore import QPointF

from ..properties import PropertySpec

from .pin_rect      import PinRect
from .property_text import PropertyTextSpec
from .anchor_point  import APName


class Block(PinRect):
    # class attributes
    _PROPERTY_SPECS = PinRect._PROPERTY_SPECS | {
        "Reference" : PropertySpec(
            type_name = "str",
            getter    = lambda self: self._reference,
            setter    = lambda self, value: setattr(self, '_reference', value)
        ),
        "Name" : PropertySpec(
            type_name = "str",
            getter    = lambda self: self._name,
            setter    = lambda self, value: setattr(self, '_name', value)
        ),
        "Path" : PropertySpec(
            type_name = "str",
            getter    = lambda self: self._path,
            setter    = lambda self, value: setattr(self, '_path', value)
        )
    }
    _PROPERTY_TEXTS = {
        "Reference" : PropertyTextSpec( APName.BottomLeft , QPointF( 0,  0 ) , APName.TopLeft    ),
        "Name"      : PropertyTextSpec( APName.TopLeft    , QPointF( 0,  0 ) , APName.BottomLeft ),
    }

    # instance attributes
    _reference : str
    _name      : str
    _path      : str

    def __init__(
        self : Self,
        p1   : QPointF | None = None,
        p2   : QPointF | None = None,
        bare : bool = False
    ) -> None:
        self._reference = ""
        self._name = ""
        self._path = ""
        super().__init__(p1, p2, bare)
