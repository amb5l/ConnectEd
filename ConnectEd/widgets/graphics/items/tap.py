"""
Tap Item.

Represents a bus tap - a transition between a bus and a scalar or sub-bus.
"Membership" property defines tapped member(s) of bus, for example:
- 7:0
- 10:2,0
- 4,0
- 3

Provides 2 entries: major and minor. Membership property text is anchored to
minor to provide visual indication of connected net seniority.
"""


from typing import Self
from enum   import StrEnum

from PyQt6.QtCore    import QLineF
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsItem

from ....app import logger

from ....core.types import DataKind

from ..properties import InherentProperty, PropertiesMixin

from .entry import EntryItem

from .mixin import ItemMixin




class TapDirection(StrEnum):
    NORTH_WEST = "north_west"
    NORTH_EAST = "north_east"
    EAST_NORTH = "east_north"
    EAST_SOUTH = "east_south"
    SOUTH_EAST = "south_east"
    SOUTH_WEST = "south_west"
    WEST_SOUTH = "west_south"
    WEST_NORTH = "west_north"


class TapItem(
    ItemMixin,
    ItemLineMixin,
    PropertiesMixin,
    QGraphicsLineItem
):
    # class attributes
    _PROPERTIES_BITS = \
        {
            "Bits" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self.bits(),
                setter = lambda self, value: self.setBits(value)
            )
        }

    # instance attributes
    _line      : QLineF
    _direction : TapDirection
    _bits      : str        # e.g. "7:0", "10:2,0", "4,0", "3"
    _entry     : EntryItem

    def __init__(
        self  : Self,
        fresh : bool = True
    ) -> None:
        QGraphicsLineItem.__init__(self, parent)
        self.initItem(fresh)
        self._line = QLineF(0, 0, 10, 10)
        self._direction = TapDirection.EAST_SOUTH
        self._bits = "?"


    def setDirection(self : Self, value : TapDirection) -> None:
        # determine self rotation and entry rotation
        match value:
            case TapDirection.NORTH_WEST : r =
            case TapDirection.NORTH_EAST :
            case TapDirection.EAST_NORTH : r = (0, 0)
            case TapDirection.EAST_SOUTH : r = (0, 0)
            case TapDirection.SOUTH_EAST : r = (0, 90)
            case TapDirection.SOUTH_WEST : r = (90, 0)
            case TapDirection.WEST_SOUTH : r = (0, -)
            case TapDirection.WEST_NORTH :

    def bits(self : Self) -> str:
        return self._bits

    def setBits(self : Self, value : str) -> None:
        # strip
        value = value.strip()
        # find and remove anything that is not a digit, colon or comma
        removals = ""
        for i, c in enumerate(value):
            if not c.isdigit() and c != ":" and c != ",":
                # remove character
                value = value[:i] + value[i+1:]
                # record removal
                removals += c
        if removals != "":
            logger().warning(f"Removed invalid characters: {removals}")
        # validate
        if value != "":
            self._bits = value
        else:
            logger().warning("Empty value")

    def rotateCW(self : Self) -> None:
        match self._direction:
            case TapDirection.NORTH_WEST : new_dir = TapDirection.NORTH_EAST
            case TapDirection.NORTH_EAST : new_dir = TapDirection.EAST_NORTH
            case TapDirection.EAST_NORTH : new_dir = TapDirection.EAST_SOUTH
            case TapDirection.EAST_SOUTH : new_dir = TapDirection.SOUTH_EAST
            case TapDirection.SOUTH_EAST : new_dir = TapDirection.SOUTH_WEST
            case TapDirection.SOUTH_WEST : new_dir = TapDirection.WEST_SOUTH
            case TapDirection.WEST_SOUTH : new_dir = TapDirection.WEST_NORTH
            case TapDirection.WEST_NORTH : new_dir = TapDirection.NORTH_WEST
        self._direction = new_dir

    def rotateCCW(self : Self) -> None:
        match self._direction:
            case TapDirection.NORTH_WEST : new_dir = TapDirection.WEST_NORTH
            case TapDirection.NORTH_EAST : new_dir = TapDirection.NORTH_WEST
            case TapDirection.EAST_NORTH : new_dir = TapDirection.EAST_SOUTH
            case TapDirection.EAST_SOUTH : new_dir = TapDirection.EAST_NORTH
            case TapDirection.SOUTH_EAST : new_dir = TapDirection.SOUTH_WEST
            case TapDirection.SOUTH_WEST : new_dir = TapDirection.SOUTH_EAST
            case TapDirection.WEST_SOUTH : new_dir = TapDirection.WEST_SOUTH
            case TapDirection.WEST_NORTH : new_dir = TapDirection.NORTH_EAST
        self._direction = new_dir

