__all__ = ["Block", "cmdPlaceBlock"]

from PyQt6.QtCore import QPointF

from ..properties import SimplePropertySpec, PropertyTextSpec

from . import KPLoc, KPDef

from .pin_rect      import PinRect, cmdPlacePinRect
from .property_text import PropertyDisplay as pd


class Block(PinRect):
    _PROPERTY_SPECS = PinRect._PROPERTY_SPECS | {
        "Reference" : SimplePropertySpec(value="", inherent=False),
        "Name"      : SimplePropertySpec(value="", inherent=False),
        "Path"      : SimplePropertySpec(value="", inherent=False)
    }
    _PROPERTY_TEXTS = {
    #   name            display     anchor           pos                cleat
        "Reference" : PropertyTextSpec( pd.VALUE  , KPLoc.BOTTOM_LEFT , QPointF( 0,  0 ) , KPLoc.TOP_LEFT    ),
        "Name"      : PropertyTextSpec( pd.VALUE  , KPLoc.TOP_LEFT    , QPointF( 0,  0 ) , KPLoc.BOTTOM_LEFT ),
    }

class cmdPlaceBlock(cmdPlacePinRect):
    pass
