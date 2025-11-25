from typing import Self

from PyQt6.QtCore    import QPointF

from ..property   import PropertySpec
from ..properties import PropertiesMixin

from . import SignalDirection, VectorRange

from .property_text import PropertyTextSpec
from .handle        import Handle
from .entry         import Entry

from .mixin            import ItemMixin
from .mixin.rotate     import ItemRotateMixin
from .mixin.handle     import ItemHandlesMixin
from .mixin.line       import ItemLineMixin
from .mixin.change     import ItemChangeMixin
from .mixin.clone      import ItemCloneMixin
from .mixin.xml        import ItemXmlMixin
from .mixin.menu       import ItemMenuMixin


class PortPinMixin(
    ItemMixin,
    ItemRotateMixin,
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
    _PROPERTY_SPECS_PORT_PIN = \
        {
            "Direction" : PropertySpec(
                kind   = "SignalDirection",
                getter = lambda self: self._direction,
                setter = lambda self, value: setattr(self, "_direction", value)
            ),
            "Range" : PropertySpec(
                kind   = "VectorRange",
                valid  = lambda self: self._range is not None,
                getter = lambda self: self._range,
                setter = lambda self, value: setattr(self, "_range", value)
            ),
            "Comment" : PropertySpec(
                getter = lambda self: self._comment,
                setter = lambda self, value: setattr(self, "_comment", value)
            )
        }
    _PROPERTY_SPECS = \
        _PROPERTY_SPECS_NAME | \
        _PROPERTY_SPECS_PORT_PIN | \
        ItemLineMixin._PROPERTY_SPECS_LINE

    # instance attributes
    _name      : str
    _comment   : str
    _direction : SignalDirection
    _range     : VectorRange
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
            self.properties["Direction"].changed.emit(value)

    def range(self : Self) -> VectorRange:
        return self._range

    def setRange(self : Self, value : VectorRange) -> None:
        self._range = value
        if hasattr(self, "properties") and "Range" in self.properties:
            self.properties["Range"].changed.emit(value)

    def comment(self : Self) -> str:
        return self._comment

    def setComment(self : Self, value : str) -> None:
        self._comment = value
        if hasattr(self, "properties") and "Comment" in self.properties:
            self.properties["Comment"].changed.emit(value)

    ############################################################################
