__all__ = ["Block", "cmdPlaceBlock"]

from typing import Self

from PyQt6.QtCore import QPointF

from ....core import Z_DRAWING

from . import KP, KPDef

from .base_rect     import BaseRectWithPins, cmdPlaceBaseRectWithPins
from .property_text import PropertyDisplay as pd


class Block(BaseRectWithPins):
    _KEY_POINTS = [KPDef(k, k != KP.CENTER, True) for k in KP.__iter__()]
    _PROPERTIES = {
    # properties with PropertyText instances
    #   name            value   display     anchor           pos                cleat
        "Reference" : ( ""    , pd.VALUE  , KP.BOTTOM_LEFT , QPointF( 0,  0 ) , KP.TOP_LEFT    ),
        "Name"      : ( ""    , pd.VALUE  , KP.TOP_LEFT    , QPointF( 0,  0 ) , KP.BOTTOM_LEFT ),
    # properties
    #   name          value
        "Path"      : ""
    }

class cmdPlaceBlock(cmdPlaceBaseRectWithPins):
    pass
