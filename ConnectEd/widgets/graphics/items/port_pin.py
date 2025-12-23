from typing import Self

from PyQt6.QtCore import QPointF

from ..property   import PropertySpec
from ..properties import PropertiesMixin

from . import SignalDirection

from .property_text import PropertyTextSpec
from .handle        import Handle
from .entry         import Entry

from .mixin        import ItemMixin
from .mixin.handle import ItemHandlesMixin
from .mixin.pen    import ItemLineMixin
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
    _PROPERTY_SPECS_NAME = \
        {
            "Name" : PropertySpec(
                getter = lambda self: self._name,
                setter = lambda self, value: setattr(self, "_name", value),
                text   = PropertyTextSpec("Name", origin="Middle Left")
            )
        }
    _PROPERTY_SPECS_DIR = \
        {
            "Dir" : PropertySpec(
                kind   = "SignalDirection",
                getter = lambda self: self._direction,
                setter = lambda self, value: setattr(self, "_direction", value)
            )
        }
    _PROPERTY_SPECS_COMMENT = \
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
    _entry     : Entry

    def initPortPin(self : Self, bare : bool = False) -> None:
        # Initialize attributes that properties will access
        self._name      = ""
        self._direction = SignalDirection.IN
        self._range     = None
        self._comment   = ""
        # Initialize the item (this sets up properties system)
        self.initItem(bare)
        # Initialize the entry
        self._entry = Entry(self)

    def initHandles(self : Self) -> None:
        self._handles = {
            "Origin" : Handle(
                name   = "Origin",
                pos    = QPointF(0, 0),
                resize = False,
                parent = self
            ),
            "Name" : Handle(
                name   = "Name",
                pos    = QPointF(self._AP_NAME_OFFSET, 0),
                resize = False,
                parent = self
            )
        }

    def name(self : Self) -> str:
        return self._name

    def setName(self : Self, value : str) -> None:
        self._name = value
        if hasattr(self, "properties") and "Name" in self.properties:
            self.properties["Name"].changed.emit(value)

    def direction(self : Self) -> SignalDirection:
        return self._direction

    def setDirection(self : Self, value : SignalDirection) -> None:
        self._direction = value
        if hasattr(self, "properties") and "Direction" in self.properties:
            self.properties["Dir"].changed.emit(value)

    def comment(self : Self) -> str:
        return self._comment

    def setComment(self : Self, value : str) -> None:
        self._comment = value
        if hasattr(self, "properties") and "Comment" in self.properties:
            self.properties["Comment"].changed.emit(value)

    ############################################################################
