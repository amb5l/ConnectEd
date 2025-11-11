from typing import Self

from PyQt6.QtCore    import QPointF

from ..properties import PropertySpec, PropertiesMixin

from . import SignalDirection, VectorRange

from .mixin        import ItemMixin
from .mixin.rotate import ItemRotateMixin
from .mixin.handle import ItemHandlesMixin
from .mixin.line   import ItemLineMixin
from .mixin.change import ItemChangeMixin
from .mixin.clone  import ItemCloneMixin
from .mixin.xml    import ItemXmlMixin
from .mixin.menu   import ItemMenuMixin

from .handle        import Handle
from .property_text import PropertyText

from .entry import Entry


class PortPinText(PropertyText):
    pass


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
                type_name = "str",
                getter    = lambda self: self._name,
                setter    = lambda self, value: setattr(self, '_name', value)
            )
        }
    _PROPERTY_SPECS_PORT_PIN = \
        {
            "Direction" : PropertySpec(
                type_name = "SignalDirection",
                getter    = lambda self: self._direction,
                setter    = lambda self, value: setattr(self, '_direction', value)
            ),
            "Range Left" : PropertySpec(
                type_name = "str",
                exists    = lambda self: self._range is not None,
                getter    = lambda self: self._range.left,
                setter    = lambda self, value: setattr(self._range, 'left', value)
            ),
            "Range Direction" : PropertySpec(
                type_name = "RangeDirection",
                exists    = lambda self: self._range is not None,
                getter    = lambda self: self._range.dir,
                setter    = lambda self, value: setattr(self._range, 'dir', value)
            ),
            "Range Right" : PropertySpec(
                type_name = "str",
                exists    = lambda self: self._range is not None,
                getter    = lambda self: self._range.right,
                setter    = lambda self, value: setattr(self._range, 'right', value)
            ),
            "Comment" : PropertySpec(
                type_name = "str",
                getter    = lambda self: self._comment,
                setter    = lambda self, value: setattr(self, '_comment', value)
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

    @classmethod
    def _getEntryClass(cls) -> type[Entry]:
        """Return the entry class."""
        raise NotImplementedError("Subclasses must implement this method")

    @classmethod
    def _getNameClass(cls) -> type[PortPinText]:
        """Return the name text class."""
        raise NotImplementedError("Subclasses must implement this method")

    @classmethod
    def _getCommentClass(cls) -> type[PortPinText]:
        """Return the comment text class."""
        raise NotImplementedError("Subclasses must implement this method")

    def initPortPin(self : Self, bare : bool = False) -> None:
        # Initialize attributes that properties will access
        self._name      = ""
        self._direction = SignalDirection.IN
        self._range     = None
        self._comment   = ""
        # Initialize the item (this sets up properties system)
        self.initItem(bare)
        # Initialize the entry
        self._entry = self._getEntryClass()(self)

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

    def direction(self : Self) -> SignalDirection:
        return self._direction

    def setDirection(self : Self, value : SignalDirection) -> None:
        self._direction = value

    def range(self : Self) -> VectorRange:
        return self._range

    def setRange(self : Self, value : VectorRange) -> None:
        self._range = value

    def comment(self : Self) -> str:
        return self._comment

    def setComment(self : Self, value : str) -> None:
        self._comment = value

    ############################################################################
