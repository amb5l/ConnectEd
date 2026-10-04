from typing import Self

from ......core.check import checked
from ......core.types import EdgeLoc

from ....items.block     import BlockItem
from ....items.block_pin import BlockPinItem

from ..cmd               import CmdBase


class CmdBlockPinBase(CmdBase):
    """Base class for all commands that work with a pin."""

    # instance attributes
    _parent : BlockItem
    _pin    : BlockPinItem

    @checked
    def __init__(
        self   : Self,
        parent : BlockItem,
        pin    : BlockPinItem
    ) -> None:
        super().__init__()
        self._parent = parent
        self._pin = pin

    @checked
    def pin(self : Self) -> BlockPinItem:
        return self._pin


class CmdBlockPinsBase(CmdBase):
    """Base class for all commands that work with multiple block pins."""

    # instance attributes
    _parent : BlockItem
    _pins   : list[BlockPinItem]

    @checked
    def __init__(
        self   : Self,
        parent : BlockItem,
        pins   : list[BlockPinItem]
    ) -> None:
        super().__init__()
        self._parent = parent
        self._pins = pins


class CmdAddBlockPin(CmdBlockPinBase):
    """Command to add a pin to a pin rect."""

    @checked
    def redo(self : Self) -> None:
        self._pin.setParentItem(self._parent)

    @checked
    def undo(self : Self) -> None:
        _dropBlockPin(self._pin)


class CmdDeleteBlockPin(CmdBlockPinBase):
    """Command to delete a pin from a pin rect."""

    @checked
    def redo(self : Self) -> None:
        _dropBlockPin(self._pin)

    @checked
    def undo(self : Self) -> None:
        self._pin.setParentItem(self._parent)


class CmdMoveBlockPins(CmdBlockPinsBase):
    """Command to move multiple pins by an offset."""

    # instance attributes
    _after  : dict[BlockPinItem, EdgeLoc] # locations after
    _before : dict[BlockPinItem, EdgeLoc] # locations before

    @checked
    def __init__(
        self   : Self,
        parent : BlockItem,
        pins   : list[BlockPinItem],
        after  : dict[BlockPinItem, EdgeLoc],
        before : dict[BlockPinItem, EdgeLoc]
    ) -> None:
        super().__init__(parent, pins)
        self._after = after
        self._before = before

    @checked
    def redo(self : Self) -> None:
        for pin in self._pins:
            pin.setLoc(self._after[pin])

    @checked
    def undo(self : Self) -> None:
        for pin in self._pins:
            pin.setLoc(self._before[pin])


def _dropBlockPin(pin : BlockPinItem) -> None:
    """Unparent a pin and take it out of the scene.

    ``setParentItem(None)`` alone leaves the pin as a top-level scene
    item, and the next save writes it as a diagram-level ``BlockPin``.
    """
    scene = pin.scene()
    pin.setParentItem(None)
    if scene is not None:
        scene.removeItem(pin)
