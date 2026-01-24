from typing import Self

from ....items import EdgeLoc

from ....items.block     import BlockItem
from ....items.block_pin import BlockPinItem

from . import CmdBase


class CmdBlockPinBase(CmdBase):
    """Base class for all commands that work with a pin."""

    # instance attributes
    _parent : BlockItem
    _pin    : BlockPinItem

    def __init__(
        self : Self,
        parent : BlockItem,
        pin    : BlockPinItem
    ):
        super().__init__()
        self._parent = parent
        self._pin = pin

    def pin(self : Self) -> BlockPinItem:
        return self._pin


class CmdBlockPinsBase(CmdBase):
    """Base class for all commands that work with multiple block pins."""

    # instance attributes
    _parent : BlockItem
    _pins   : list[BlockPinItem]

    def __init__(
        self : Self,
        parent : BlockItem,
        pins   : list[BlockPinItem]
    ):
        super().__init__()
        self._parent = parent
        self._pins = pins


class CmdAddBlockPin(CmdBlockPinBase):
    """Command to add a pin to a pin rect."""

    def redo(self : Self) -> None:
        self._pin.setParentItem(self._parent)

    def undo(self : Self) -> None:
        self._pin.setParentItem(None)


class CmdDeleteBlockPin(CmdBlockPinBase):
    """Command to delete a pin from a pin rect."""

    def redo(self : Self) -> None:
        self._pin.setParentItem(None)

    def undo(self : Self) -> None:
        self._pin.setParentItem(self._parent)


class CmdMoveBlockPins(CmdBlockPinsBase):
    """Command to move multiple pins by an offset."""

    # instance attributes
    _after  : dict[BlockPinItem, EdgeLoc] # locations after
    _before : dict[BlockPinItem, EdgeLoc] # locations before

    def __init__(
        self   : Self,
        parent : BlockItem,
        pins   : list[BlockPinItem],
        after  : dict[BlockPinItem, EdgeLoc],
        before : dict[BlockPinItem, EdgeLoc]
    ):
        super().__init__(parent, pins)
        self._after = after
        self._before = before

    def redo(self : Self) -> None:
        for pin in self._pins:
            pin.setLoc(self._after[pin])

    def undo(self : Self) -> None:
        for pin in self._pins:
            pin.setLoc(self._before[pin])
