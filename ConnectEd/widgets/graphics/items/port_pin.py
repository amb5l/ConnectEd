from typing import Self

from PyQt6.QtCore import QPointF

from ..property   import PropertySpec
from ..properties import PropertiesMixin

from . import SignalDirection

from .property_text import PropertyTextSpec
from .handle        import HandleItem
from .entry         import EntryItem

from .mixin        import ItemMixin
from .mixin.handle import ItemHandlesMixin
from .mixin.line   import ItemLineMixin
from .mixin.change import ItemChangeMixin
from .mixin.clone  import ItemCloneMixin
from .mixin.xml    import ItemXmlMixin
from .mixin.menu   import ItemMenuMixin


class PortPinMixin(
    ItemMixin,
    ItemHandlesMixin,
    ItemLineMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin
):
    # class attributes
    _AP_NAME_OFFSET = 1.5
    _INHERENT_PROPERTIES_NAME = \
        {
            "Name" : PropertySpec(
                getter = lambda self: self._name,
                setter = lambda self, value: setattr(self, "_name", value),
                text   = PropertyTextSpec("Name", origin="Middle Left")
            )
        }
    _INHERENT_PROPERTIES_DIR = \
        {
            "Dir" : PropertySpec(
                kind   = "SignalDirection",
                getter = lambda self: self._direction,
                setter = lambda self, value: setattr(self, "_direction", value)
            )
        }
    _INHERENT_PROPERTIES_COMMENT = \
        {
            "Comment" : PropertySpec(
                valid  = lambda self: self._comment != "",
                getter = lambda self: self._comment,
                setter = lambda self, value: setattr(self, "_comment", value)
            )
        }

    # instance attributes
    _name      : str
    _direction : SignalDirection
    _comment   : str
    _entry     : EntryItem

    def initPortPin(self : Self, fresh : bool) -> None:
        # Initialize attributes that properties will access
        self._name      = ""
        self._direction = SignalDirection.IN
        self._range     = None
        self._comment   = ""
        # Initialize the item (this sets up properties system)
        self.initItem(fresh)
        # Initialize the entry
        self._entry = EntryItem(self)

    def initHandles(self : Self) -> None:
        self._handles = {
            "Origin" : HandleItem(
                name   = "Origin",
                pos    = QPointF(0, 0),
                kind   = "move",
                parent = self
            ),
            "Name" : HandleItem(
                name   = "Name",
                pos    = QPointF(self._AP_NAME_OFFSET, 0),
                kind   = "move",
                parent = self
            )
        }

    def name(self : Self) -> str:
        return self._name

    def setName(self : Self, value : str) -> None:
        self._name = value
        self.updateProperties("Name")

    def direction(self : Self) -> SignalDirection:
        return self._direction

    def setDirection(self : Self, value : SignalDirection) -> None:
        self._direction = value
        self.updateProperties("Dir")

    def comment(self : Self) -> str:
        return self._comment

    def setComment(self : Self, value : str) -> None:
        self._comment = value
        self.updateProperties("Comment")

    ############################################################################
