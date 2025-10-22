from typing import Self

from PyQt6.QtCore import QPointF

from ....items import EdgeLoc, ItemMixin

from ....items.block      import Block
from ....items.rectangle  import Rectangle
from ....items.text       import Text
from ....items.text_block import TextBlock
from ....items.port       import Port
from ....items.block_pin  import BlockPin

from . import cmdBase, cmdSceneBase


class cmdPlaceBase(cmdSceneBase):
    """Base class for commands that place an item."""

    # class attributes
    _CLASS : ItemMixin
    _SELECTION = True

    # instance attributes
    _item : ItemMixin

    def begin(self : Self, pos : QPointF) -> None:
        super().begin() # preserve selection set
        self._item = self._CLASS(pos)
        self._item.setSelected(True)
        self._scene.addItem(self._item)

    @property
    def item(self : Self) -> ItemMixin:
        return self._item

    def redo(self : Self) -> None:
        if self._item.scene() != self._scene:
            self._scene.addItem(self._item)

    def undo(self : Self) -> None:
        super().undo() # restore selection set
        self._scene.removeItem(self._item)


class cmdPlacePort(cmdPlaceBase):
    _CLASS = Port


class cmdPlaceBlock(cmdPlaceBase):
    _CLASS = Block


class cmdPlaceRectangle(cmdPlaceBase):
    _CLASS = Rectangle


class cmdPlaceText(cmdPlaceBase):
    _CLASS = Text


class cmdPlaceTextBlock(cmdPlaceBase):
    _CLASS = TextBlock


class cmdPlaceBlockPin(cmdBase):
    """Base class for commands that place a pin."""

    # instance attributes
    _parent : Block
    _loc    : EdgeLoc

    def __init__(self : Self, parent : Block, loc : EdgeLoc):
        super().__init__(parent.scene())
        self._parent = parent
        self._loc    = loc

    def begin(self : Self, pos : QPointF) -> None:
        raise NotImplementedError


class cmdPlaceBlockPin(cmdPlaceBlockPin):
    _CLASS = BlockPin

##class cmdPlaceSymbolPin(cmdPlacePinBase):
#    _CLASS = SymbolPin
