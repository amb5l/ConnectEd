__all__ = ["Block", "cmdPlaceBlock"]

from typing import Self

from PyQt6.QtCore import QPointF

from ....core import Z_DRAWING

from . import KPLoc as kp

from .base_rect import BaseRectangle, cmdPlaceBaseRectangle
from .property  import PropertyDisplay as pd

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


class Block(BaseRectangle):
    Z = Z_DRAWING
    _PROPERTIES = {
    #   name            value  display     anchor           pos                cleat
        "Reference" : ( ""   , pd.VALUE  , kp.BOTTOM_LEFT , QPointF( 0,  0 ) , kp.TOP_LEFT    ),
        "Name"      : ( ""   , pd.VALUE  , kp.TOP_LEFT    , QPointF( 0,  0 ) , kp.BOTTOM_LEFT ),
        "Path"      : ( ""   , pd.HIDDEN , kp.TOP_LEFT    , QPointF( 0, 10 ) , kp.BOTTOM_LEFT )
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
