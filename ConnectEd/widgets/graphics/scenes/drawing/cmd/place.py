from typing import Self

from PyQt6.QtCore import QPointF


from ....items import EdgeLoc, ElementMixin

from ....items.pin_rect   import PinRect
from ....items.block      import Block
from ....items.rectangle  import Rectangle
from ....items.text       import Text
from ....items.text_block import TextBlock

from ....items.port_pin.port      import Port
from ....items.port_pin.block_pin import BlockPin

from . import cmdBase, cmdSceneBase

class cmdPlaceBase(cmdSceneBase):
    """Base class for commands that place an element."""

    # class attributes
    _PREVIEW   = True
    _SELECTION = True
    _CLASS : ElementMixin

    # instance attributes
    _element : ElementMixin

    def begin(self : Self, pos : QPointF) -> None:
        super().begin() # preserve selection set
        self._element = self._CLASS(pos)
        self._element.setSelected(True)
        self._scene.addItem(self._element)

    @property
    def element(self : Self) -> ElementMixin:
        return self._element

    def redo(self : Self) -> None:
        if self._element.scene() != self._scene:
            self._scene.addItem(self._element)

    def undo(self : Self) -> None:
        super().undo() # restore selection set
        self._scene.removeItem(self._element)

class cmdPlacePort(cmdPlaceBase):
    _CLASS = Port

class cmdPlacePinRect(cmdPlaceBase):
    _CLASS = PinRect

class cmdPlaceBlock(cmdPlacePinRect):
    _CLASS = Block

class cmdPlaceRectangle(cmdPlaceBase):
    _CLASS = Rectangle

class cmdPlaceText(cmdPlaceBase):
    _CLASS = Text

class cmdPlaceTextBlock(cmdPlaceBase):
    _CLASS = TextBlock

class cmdPlacePin(cmdBase):
    """Base class for commands that place a pin."""

    # instance attributes
    _parent : PinRect
    _loc    : EdgeLoc

    def __init__(self : Self, parent : PinRect, loc : EdgeLoc):
        super().__init__(parent.scene())
        self._parent = parent
        self._loc    = loc

    def begin(self : Self, pos : QPointF) -> None:
        raise NotImplementedError

class cmdPlaceBlockPin(cmdPlacePin):
    _CLASS = BlockPin

##class cmdPlaceSymbolPin(cmdPlacePinBase):
#    _CLASS = SymbolPin