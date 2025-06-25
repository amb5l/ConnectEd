__all__ = ["Block", "cmdPlaceBlock"]

from ....core import Z_DRAWING

from .base_rect import BaseRectangle, cmdPlaceBaseRectangle


class Block(BaseRectangle):
    Z = Z_DRAWING

class cmdPlaceBlock(cmdPlaceBaseRectangle):
    pass
