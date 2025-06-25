__all__ = ["Rectangle", "cmdPlaceRectangle"]

from ....core import Z_DRAWING

from .base_rect import BaseRectangle, cmdPlaceBaseRectangle


class Rectangle(BaseRectangle):
    Z = Z_DRAWING

class cmdPlaceRectangle(cmdPlaceBaseRectangle):
    pass
