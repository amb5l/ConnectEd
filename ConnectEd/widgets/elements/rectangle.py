__all__ = ['Rectangle', 'cmdPlaceRectangle', 'cmdResizeRectangle']

from ...core    import Z_DRAWING

from .base_rect import \
    BaseRectangle, cmdPlaceBaseRectangle, cmdResizeBaseRectangle


class Rectangle(BaseRectangle):
    Z = Z_DRAWING

class cmdPlaceRectangle(cmdPlaceBaseRectangle):
    pass

class cmdResizeRectangle(cmdResizeBaseRectangle):
    pass
