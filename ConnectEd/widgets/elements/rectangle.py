__all__ = ['Rectangle', 'cmdRectangle']

from ...core    import Z_DRAWING

from .base_rect import BaseRectangle, cmdBaseRectangle


class Rectangle(BaseRectangle):
    Z = Z_DRAWING

class cmdRectangle(cmdBaseRectangle):
    pass
