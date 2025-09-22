from typing import Self

from PyQt6.QtCore    import QPointF

from ...properties import PropertySpec, PropertiesMixin

from .. import SignalDirection, VectorRange

from ..mixin        import ElementMixin
from ..mixin.anchor import ElementAnchorPointsMixin
from ..mixin.line   import ElementLineMixin
from ..mixin.change import ElementChangeMixin
from ..mixin.clone  import ElementCloneMixin
from ..mixin.xml    import ElementXmlMixin
from ..mixin.menu   import ElementMenuMixin

from ..property_text import PropertyText, PropertyTextSpec
from ..anchor_point  import APName, AnchorPoint

from .node import Node


class PortPinText(PropertyText):
    def compensateRotation(self : Self, angle : float) -> None:
        self.setTransformOriginPoint(self._brect.center())
        self.setRotation(180 if 45 <= angle < 225 else 0)


class PortPinMixin(
    ElementMixin,
    ElementAnchorPointsMixin,
    ElementLineMixin,
    ElementChangeMixin,
    ElementCloneMixin,
    ElementXmlMixin,
    ElementMenuMixin,
    PropertiesMixin
):
    # class attributes
    _NAME_OFFSET = 1.5
    _PROPERTY_SPECS = \
        {
            "Name" : PropertySpec(
                type_name = "str",
                getter    = lambda self: self._name,
                setter    = lambda self, value: setattr(self, '_name', value)
            ),
            "Direction" : PropertySpec(
                type_name = "SignalDirection",
                getter    = lambda self: self._direction,
                setter    = lambda self, value: setattr(self, '_direction', value)  # Use property setter
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
        } | \
        ElementLineMixin._PROPERTY_SPECS_LINE

    # instance attributes
    _name      : str
    _comment   : str
    _direction : SignalDirection
    _range     : VectorRange
    _node      : Node

    @classmethod
    def _getNodeClass(cls) -> type[Node]:
        """Return the node class. Subclasses should override this."""
        return Node

    @classmethod
    def _getNameClass(cls) -> type[PortPinText]:
        """Return the name text class. Subclasses should override this."""
        return PortPinText

    @classmethod
    def _getCommentClass(cls) -> type[PortPinText]:
        """Return the comment text class. Subclasses should override this."""
        return PortPinText

    @classmethod
    def _getPropertyTexts(cls) -> dict[str, PropertyTextSpec]:
        return {
            "Name" : PropertyTextSpec(
                anchor  = APName.CenterLeft,
                pos     = QPointF(0, 0),
                cleat   = APName.Name,
                _class  = cls._getNameClass()
            ),
        }

    def initPortPin(self : Self) -> None:
        # Initialize attributes that properties will access
        self._name      = ""
        self._direction = SignalDirection.IN
        self._range     = None
        self._comment   = ""
        # Initialize the element (this sets up properties system)
        self.initElement()
        # Initialize the node
        self._node = self._getNodeClass()(self)

    def initAnchorPoints(self : Self) -> None:
        self._anchor_points = {
            APName.Origin : AnchorPoint(
                name   = APName.Origin,
                pos    = QPointF(0, 0),
                resize = False,
                parent = self
            ),
            APName.Name : AnchorPoint(
                name   = APName.Name,
                pos    = QPointF(self._NAME_OFFSET, 0),
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
