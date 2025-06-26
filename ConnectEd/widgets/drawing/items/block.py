__all__ = ["Block", "cmdPlaceBlock"]

from typing import Self

from ....core import Z_DRAWING

from .base_rect import BaseRectangle, cmdPlaceBaseRectangle

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


class Block(BaseRectangle):
    Z = Z_DRAWING
    _PROPERTIES = {
        "Reference" : "", # VHDL instance label
        "Name"      : "", # VHDL component or entity name
        "Path"      : ""  # path to HDL source or ConnectEd diagram
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
