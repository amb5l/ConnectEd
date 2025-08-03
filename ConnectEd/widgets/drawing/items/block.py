__all__ = ["Block", "cmdPlaceBlock"]

from PyQt6.QtCore import QPointF

from ..properties import PropertySpec, PropertyTextSpec

from .pin_rect      import PinRect, cmdPlacePinRect
from .property_text import PropertyDisplay as pd


class Block(PinRect):
    _PROPERTY_SPECS = PinRect._PROPERTY_SPECS | {
        "Reference" : PropertySpec(custom=True),
        "Name"      : PropertySpec(custom=True),
        "Path"      : PropertySpec(custom=True)
    }
    _PROPERTY_TEXTS = {
    #   name            display     anchor           pos                cleat
        "Reference" : PropertyTextSpec( pd.VALUE  , "Bottom Left" , QPointF( 0,  0 ) , "Top Left"    ),
        "Name"      : PropertyTextSpec( pd.VALUE  , "Top Left"    , QPointF( 0,  0 ) , "Bottom Left" ),
    }

class cmdPlaceBlock(cmdPlacePinRect):
    pass
