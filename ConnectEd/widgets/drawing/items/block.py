__all__ = ["Block", "cmdPlaceBlock"]

from typing import Self

from PyQt6.QtCore import QPointF

from ....core import Z_DRAWING

from . import KP

from .base_rect     import BaseRectangle, cmdPlaceBaseRectangle
from .property_text import PropertyDisplay as pd

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


class Block(BaseRectangle):
    Z = Z_DRAWING
    _PROPERTIES = {
    #   name            value  display     anchor           pos                cleat
        "Reference" : ( ""   , pd.VALUE  , KP.BOTTOM_LEFT , QPointF( 0,  0 ) , KP.TOP_LEFT    ),
        "Name"      : ( ""   , pd.VALUE  , KP.TOP_LEFT    , QPointF( 0,  0 ) , KP.BOTTOM_LEFT ),
        "Path"      : ( ""   , pd.HIDDEN , KP.TOP_LEFT    , QPointF( 0, 10 ) , KP.BOTTOM_LEFT )
    }
    _MENU_ITEM_NAMES = [
        "Properties..."
    ] + BaseRectangle._MENU_ITEM_NAMES

    def ctxMenuProperties(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        view.editProperties(self)

class cmdPlaceBlock(cmdPlaceBaseRectangle):
    pass
