from typing import Self, Optional

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsPathItem, \
                            QWidget, QStyleOptionGraphicsItem, QStyle
from PyQt6.QtGui     import QPainterPath, QPainter

from ...properties import PropertySpec, PropertiesMixin

from .. import APType, SignalDirection, VectorRange

from ..mixin        import ElementMixin
from ..mixin.anchor import ElementAnchorPointsMixin
from ..mixin.line   import ElementLineMixin
from ..mixin.fill   import ElementFillMixin
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
        r = self.getTotalRotation()
        self.setRotation(180 if 45 <= angle < 225 else 0)


class PortPinMixin(
    ElementMixin,
    ElementAnchorPointsMixin,
    ElementLineMixin,
    ElementFillMixin,
    ElementChangeMixin,
    ElementCloneMixin,
    ElementXmlMixin,
    ElementMenuMixin,
    PropertiesMixin
):
    # class attributes
    _NODE_CLASS    = Node        # subclass to override
    _NAME_CLASS    = PortPinText # subclass to override
    _COMMENT_CLASS = PortPinText # subclass to override
    _NAME_OFFSET   = 1.5
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
        ElementLineMixin._PROPERTY_SPECS_LINE | \
        ElementFillMixin._PROPERTY_SPECS_FILL
    # instance attributes
    _direction : SignalDirection
    _range     : VectorRange
    _node      : _NODE_CLASS

    @classmethod
    def _getPropertyTexts(cls) -> dict[str, PropertyTextSpec]:
        return {
            "Name" : PropertyTextSpec(
                anchor  = "Center Left",
                pos     = QPointF(0, 0),
                cleat   = "Name",
                _class  = cls._NAME_CLASS
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
        self.node = self._NODE_CLASS(self)

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
        if isinstance(self, PortPinArrow):
            match value:
                case SignalDirection.IN:  self.setPath(self._path_in)
                case SignalDirection.OUT: self.setPath(self._path_out)
                case _:                   self.setPath(self._path_bi)

    @property
    def range(self : Self) -> VectorRange:
        return self._range

    @range.setter
    def range(self : Self, value : VectorRange) -> None:
        self._range = value

    @property
    def node(self : Self) -> _NODE_CLASS:
        return self._node

    @node.setter
    def node(self : Self, value : _NODE_CLASS) -> None:
        self._node = value

    def getMenuItems(self : Self) -> list[str]:
        return ["Edit"]

    def ctxMenuEdit(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        view.editPort(self)


class PortPinArrow(PortPinMixin, QGraphicsPathItem):
    """Base QGraphicsItem class for ports and block pins."""

    # class attributes
    _SIZE         = 8
    _PATH_AWAY    = [(1,0), (0.5,-0.5), (0,-0.5), (0,0.5), (0.5,0.5)]
    _PATH_TOWARDS = [(0,0), (0.5,-0.5), (1,-0.5), (1,0.5), (0.5,0.5)]
    _PATH_BI      = [(0,0), (0.5,-0.5), (1,0), (0.5,0.5)]
    _PATH_IN      : list[tuple[float | int, float | int]] # subclass to define
    _PATH_OUT     : list[tuple[float | int, float | int]] # subclass to define

    # instance attributes
    _size     : float
    _path_in  : QPainterPath
    _path_out : QPainterPath
    _path_bi  : QPainterPath

    def __init__(self : Self, parent : Optional[QGraphicsItem] = None) -> None:
        QGraphicsPathItem.__init__(self, parent)
        self._size = self._SIZE
        self.initPortPin()
        self.onSettingsChange()

    def onSettingsChange(self : Self) -> None:
        """Rebuild paths when settings change."""
        self._path_in  = self._buildPath(self._PATH_IN)
        self._path_out = self._buildPath(self._PATH_OUT)
        self._path_bi  = self._buildPath(self._PATH_BI)
        self.direction = self._direction
        self.getAnchorPoint("Name").setPos(self._size + self._NAME_OFFSET, 0)

    def _buildPath(self : Self, points : list[tuple[int, int]]) -> QPainterPath:
        s = self._size
        p = QPainterPath()
        p.moveTo(s * QPointF(*points[0]))
        for point in points[1:]:
            p.lineTo(s * QPointF(*point))
        p.closeSubpath()
        return p

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : Optional[QWidget] = None
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Selected
        QGraphicsPathItem.paint(self, painter, option, widget)
