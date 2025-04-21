__all__ = ["Text", "cmdPlaceText"]

from ...core    import Z_DRAWING

from .base_text import BaseText, cmdPlaceBaseText


class Text(BaseText):
    Z = Z_DRAWING

class cmdPlaceText(cmdPlaceBaseText):
    pass
