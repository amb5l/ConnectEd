from typing import Self

from PyQt6.QtCore    import QPointF

from ...properties import PropertySpec, PropertiesMixin

from .. import APType, SignalDirection, VectorRange

from ..mixin        import ElementMixin
from ..mixin.anchor import ElementAnchorPointsMixin
from ..mixin.line   import ElementLineMixin
from ..mixin.change import ElementChangeMixin
from ..mixin.clone  import ElementCloneMixin
from ..mixin.xml    import ElementXmlMixin
from ..mixin.menu   import ElementMenuMixin

from ..property_text import PropertyText, PropertyTextSpec
from ..anchor_point  import AnchorPoint

from .node import Node

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...views.drawing import DrawingView


class PortPinText(PropertyText):
    def compensateRotation(self, angle : float) -> None:
        self.setTransformOriginPoint(self._brect.center())
        #r = self.getTotalRotation()
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
            "Name" : PropertySpec(),
            "Direction" : PropertySpec(
                type_name = "SignalDirection",
                getter    = lambda self: self._direction,
                setter    = lambda self, value: setattr(self, 'direction', value)  # Use property setter
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
            "Comment" : PropertySpec()
        } | \
        ElementLineMixin._PROPERTY_SPECS_LINE
    # instance attributes
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
                anchor  = "Center Left",
                pos     = QPointF(0, 0),
                cleat   = "Name",
                _class  = cls._getNameClass()
            ),
        }

    def initPortPin(self : Self) -> None:
        # Initialize attributes that properties will access
        self._direction = SignalDirection.IN
        self._range     = None
        self._node      = None
        # Initialize the element (this sets up properties system)
        self.initElement()
        # Set properties that require the property system
        self.name = ""
        self.comment = ""
        # Initialize the node
        self.node = self._getNodeClass()(self)

    def initAnchorPoints(self : Self) -> None:
        self._anchor_points = {
            "Origin" : AnchorPoint(
                name   = "Origin",
                type   = APType.Mover,
                pos    = QPointF(0, 0),
                parent = self
            ),
            "Name" : AnchorPoint(
                name   = "Name",
                type   = APType.Cleat,
                pos    = QPointF(self._NAME_OFFSET, 0),
                parent = self
            )
        }

    @property
    def name(self : Self) -> str:
        return self.getPropertyValue("Name")

    @name.setter
    def name(self : Self, value : str) -> None:
        self.setPropertyValue("Name", value)

    @property
    def direction(self : Self) -> SignalDirection:
        return self._direction

    @direction.setter
    def direction(self : Self, value : SignalDirection) -> None:
        self._direction = value

    @property
    def range(self : Self) -> VectorRange:
        return self._range

    @range.setter
    def range(self : Self, value : VectorRange) -> None:
        self._range = value

    @property
    def node(self : Self) -> Node:
        return self._node

    @node.setter
    def node(self : Self, value : Node) -> None:
        self._node = value

    def getMenuItems(self : Self) -> list[str]:
        return ["Edit"]

    def ctxMenuEdit(
        self    : Self,
        _checked : bool,
        view    : "DrawingView"
    ) -> None:
        view.editPort(self)
