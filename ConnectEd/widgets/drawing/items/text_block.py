__all__ = ["TextBlock", "cmdPlaceTextBlock"]

from ....core    import Z_DRAWING

from .base_text_block import BaseTextBlock, cmdPlaceBaseTextBlock


class TextBlock(BaseTextBlock):
    Z = Z_DRAWING

class cmdPlaceTextBlock(cmdPlaceBaseTextBlock):
    pass
