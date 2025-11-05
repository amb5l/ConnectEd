from typing import Self

from PyQt6.QtCore    import QPointF

from ..properties import PropertySpec, PropertiesMixin

from . import SignalDirection, VectorRange

from .mixin        import ItemMixin
from .mixin.rotate import ItemRotateMixin
from .mixin.anchor import ItemAnchorPointsMixin
from .mixin.line   import ItemLineMixin
from .mixin.change import ItemChangeMixin
from .mixin.clone  import ItemCloneMixin
from .mixin.xml    import ItemXmlMixin
from .mixin.menu   import ItemMenuMixin

from .property_text import PropertyText, PropertyTextSpec
from .anchor_point  import AnchorPoint

from .entry import Entry


class PortPinText(PropertyText):
    pass


class PortPinMixin(
    ItemMixin,
    ItemRotateMixin,
    ItemAnchorPointsMixin,
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

    @classmethod
    def _getPropertyTexts(cls) -> dict[str, PropertyTextSpec]:
        return {
            "Name" : PropertyTextSpec(
                anchor  = "Center Left",
                pos     = QPointF(0, 0),
                cleat   = "Name",
                _class  = cls._getNameClass()
            ),
        }

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

    def initAnchorPoints(self : Self) -> None:
        self._anchor_points = {
            "Origin" : AnchorPoint(
                name   = "Origin",
                pos    = QPointF(0, 0),
                resize = False,
                parent = self
            ),
            "Name" : AnchorPoint(
                name   = "Name",
                pos    = QPointF(self._AP_NAME_OFFSET, 0),
                resize = False,
                parent = self
            )
        }

    ############################################################################
    # convenience properties

    @property
    def name(self : Self) -> str:
        return self.getPropertyValue("Name")

    @name.setter
    def name(self : Self, value : str) -> None:
        self.setPropertyValue("Name", value)

    @property
    def direction(self : Self) -> SignalDirection:
        return self.getPropertyValue("Direction")

    @direction.setter
    def direction(self : Self, value : SignalDirection) -> None:
        self.setPropertyValue("Direction", value)

    @property
    def range(self : Self) -> VectorRange:
        return self._range

    @range.setter
    def range(self : Self, value : VectorRange) -> None:
        self._range = value
        self.onPropertyChange()

    @property
    def comment(self : Self) -> str:
        return self.getPropertyValue("Comment")

    @comment.setter
    def comment(self : Self, value : str) -> None:
        self.setPropertyValue("Comment", value)

    ############################################################################
