__all__ = [
    "cmdPlacePort",
    "cmdPlacePinRect",
    "cmdPlaceBlock",
    "cmdPlaceBlockPin",
    "cmdPlaceRectangle",
    "cmdPlaceText",
    "cmdPlaceTextBlock"
]

from ... import Port,      \
                PinRect,   \
                Block,     \
                BlockPin,  \
                Rectangle, \
                Text,      \
                TextBlock

from .cmd import cmdPlaceElement


class cmdPlacePort(cmdPlaceElement):
    _CLASS = Port

class cmdPlacePinRect(cmdPlaceElement):
    _CLASS = PinRect

class cmdPlaceBlock(cmdPlacePinRect):
    _CLASS = Block

class cmdPlaceBlockPin(cmdPlaceElement):
    _CLASS = BlockPin

class cmdPlaceRectangle(cmdPlaceElement):
    _CLASS = Rectangle

class cmdPlaceText(cmdPlaceElement):
    _CLASS = Text

class cmdPlaceTextBlock(cmdPlaceElement):
    _CLASS = TextBlock
