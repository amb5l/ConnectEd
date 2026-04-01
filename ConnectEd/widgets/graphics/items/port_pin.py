from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QGraphicsPathItem

from ....core.types import Direction, DataKind

from ..properties import InherentProperty, PropertiesMixin

from .vertex import EntryItem

from .mixin        import ItemMixin
from .mixin.line   import ItemLineMixin
from .mixin.fill   import ItemFillMixin
from .mixin.change import ItemChangeMixin
from .mixin.clone  import ItemCloneMixin
from .mixin.xml    import ItemXmlMixin
from .mixin.menu   import ItemMenuMixin


class PortPinMixin(
    ItemMixin,
    ItemLineMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin
):
    # class attributes
    _PIN_NAME_OFFSET = 1.5
    _PROPERTIES_NAME = \
        {
            "Name" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self._name,
                setter = lambda self, value: setattr(self, "_name", value),
            )
        }
    _PROPERTIES_DIR = \
        {
            "Dir" : InherentProperty(
                kind   = DataKind.DIRECTION,
                getter = lambda self: self._direction,
                setter = lambda self, value: setattr(self, "_direction", value)
            )
        }
    _PROPERTIES_COMMENT = \
        {
            "Comment" : InherentProperty(
                kind   = DataKind.STR,
                worthy = lambda self: self._comment != "",
                getter = lambda self: self._comment,
                setter = lambda self, value: setattr(self, "_comment", value)
            )
        }
    _PEN_CAP_STYLE  = Qt.PenCapStyle.SquareCap
    _PEN_JOIN_STYLE = Qt.PenJoinStyle.MiterJoin

    # instance attributes
    _name      : str
    _direction : Direction
    _comment   : str
    _entry     : EntryItem

    def initPortPin(self : Self | QGraphicsPathItem, fresh : bool) -> None:
        # Initialize attributes that properties will access
        self._name      = ""
        self._direction = Direction.IN
        self._range     = None
        self._comment   = ""
        # Initialize the item (this sets up properties system)
        self.initItem(fresh)
        # Initialize the entry
        self._entry = EntryItem(parent=self)

    def initHandles(self : Self) -> None:
        raise NotImplementedError("Subclass must implement this method")

    def name(self : Self) -> str:
        return self._name

    def setName(self : Self, value : str) -> None:
        self._name = value
        self.signalPropertyChanges("Name")

    def direction(self : Self) -> Direction:
        return self._direction

    def setDirection(self : Self, value : Direction) -> None:
        self._direction = value
        self.signalPropertyChanges("Dir")

    def comment(self : Self) -> str:
        return self._comment

    def setComment(self : Self, value : str) -> None:
        self._comment = value
        self.signalPropertyChanges("Comment")

    ############################################################################
