__all__ = ["TextLine", "cmdPlaceTextLine"]

from ....core    import Z_DRAWING

from .base_text_line import BaseTextLine, cmdPlaceBaseTextLine


class TextLine(BaseTextLine):
    Z = Z_DRAWING

class cmdPlaceTextLine(cmdPlaceBaseTextLine):
    pass
