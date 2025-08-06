from typing import Self

from PyQt6.QtCore    import QPointF

from pyTooling.Decorators import export

from ....items import EdgeLoc, ElementMixin

from ....items.pin_rect   import PinRect
from ....items.port_pin   import Port, BlockPin
from ....items.block      import Block
from ....items.rectangle  import Rectangle
from ....items.text       import Text
from ....items.text_block import TextBlock

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

@export
class cmdPlacePort(cmdPlaceBase):
    _CLASS = Port

@export
class cmdPlacePinRect(cmdPlaceBase):
    _CLASS = PinRect

@export
class cmdPlaceBlock(cmdPlacePinRect):
    _CLASS = Block

@export
class cmdPlaceRectangle(cmdPlaceBase):
    _CLASS = Rectangle

@export
class cmdPlaceText(cmdPlaceBase):
    _CLASS = Text

@export
class cmdPlaceTextBlock(cmdPlaceBase):
    _CLASS = TextBlock

@export
class cmdPlaceBasePin(cmdBase):
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

@export
class cmdPlaceBlockPin(cmdPlaceBasePin):
    _CLASS = BlockPin

#@export
#class cmdPlaceSymbolPin(cmdPlacePinBase):
#    _CLASS = SymbolPin