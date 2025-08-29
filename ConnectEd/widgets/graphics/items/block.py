from PyQt6.QtCore import QPointF

from ..properties import PropertySpec

from .pin_rect      import PinRect
from .property_text import PropertyTextSpec

class Block(PinRect):
    _PROPERTY_SPECS = PinRect._PROPERTY_SPECS | {
        "Reference" : PropertySpec(),
        "Name"      : PropertySpec(),
        "Path"      : PropertySpec()
    }
    _PROPERTY_TEXTS = {
        "Reference" : PropertyTextSpec( "Bottom Left" , QPointF( 0,  0 ) , "Top Left"    ),
        "Name"      : PropertyTextSpec( "Top Left"    , QPointF( 0,  0 ) , "Bottom Left" ),
    }
