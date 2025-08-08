from typing import Self, Optional

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PyQt6.QtGui     import QPainter, QPainterPath

from ....core.log import logger

from ..properties import PropertySpec, PropertiesMixin

from . import APType, EdgeLoc, SignalDirection, VectorRange, \
              ElementMixin, \
              ElementPosMixin, \
              ElementLocMixin, \
              ElementBoundShapeMixin, \
              ElementChangeMixin, \
              ElementCloneMixin, \
              ElementXmlMixin, \
              ElementMenuMixin

from .node          import Node
from .arrow         import Arrow
from .anchor_point  import AnchorPoint
from .property_text import PropertyTextSpec, PropertyText

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView
    from .pin_rect import PinRect
    from .block    import Block


class PortPinText(PropertyText):
    def compensateRotation(self, angle : float) -> None:
        self.setTransformOriginPoint(self._brect.center())
        r = self.getTotalRotation()
        self.setRotation(180 if 45 <= angle < 225 else 0)

class BasePortPin(
    ElementMixin,
    ElementBoundShapeMixin,
    ElementChangeMixin,
    ElementCloneMixin,
    ElementXmlMixin,
    ElementMenuMixin,
    PropertiesMixin,
    QGraphicsItem
):
    # class variables
    _NODE_CLASS = Node
    _PROPERTY_SPECS = {
        "Name" : PropertySpec(),
        "Direction" : PropertySpec(
            type_name = "SignalDirection",
            getter    = lambda self: self.direction,
            setter    = lambda self, value: setattr(self, 'direction', value)
        ),
        "Range Left" : PropertySpec(
            type_name = "str",
            exists    = lambda self: self.range is not None,
            getter    = lambda self: self.range.left,
            setter    = lambda self, value: setattr(self.range, 'left', value)
        ),
        "Range Direction" : PropertySpec(
            type_name = "RangeDirection",
            exists    = lambda self: self.range is not None,
            getter    = lambda self: self.range.dir,
            setter    = lambda self, value: setattr(self.range, 'dir', value)
        ),
        "Range Right" : PropertySpec(
            type_name = "str",
            exists    = lambda self: self.range is not None,
            getter    = lambda self: self.range.right,
            setter    = lambda self, value: setattr(self.range, 'right', value)
        ),
        "Comment" : PropertySpec()
    }
    _NAME_CLASS = PortPinText
    _COMMENT_CLASS = PortPinText
    _NAME_OFFSET = 1.5

    @classmethod
    def _getPropertyTexts(cls):
        return {
            "Name" : PropertyTextSpec("Center Left", QPointF(0, 0), "Name", _class=cls._NAME_CLASS)
        }

    # instance attributes
    _direction : SignalDirection
    _range     : VectorRange
    _node      : Node

    def __init__(
        self      : Self,
        name      : str                   = "",
        direction : SignalDirection       = SignalDirection.IN,
        range     : Optional[VectorRange] = None,
        bare      : bool                  = False
    ) -> None:
        QGraphicsItem.__init__(self)
        self.setFlag( self.GraphicsItemFlag.ItemHasNoContents , True )
        ElementMixin.initElement(self, bare)
        self._direction = direction
        self._range = range
        self._node = self._NODE_CLASS(self)

    def onSelectionChange(self : Self, selected : bool) -> None:
        self._node.setSelected(selected)

    def getMenuItems(self : Self) -> list[str]:
        return ["Edit"]

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
                type   = APType.Static,
                pos    = QPointF(self._NAME_OFFSET, 0),
                parent = self
            )
        }

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : Optional[QWidget] = None
    ) -> None:
        logger.error("BasePortPin.paint() should never be called")

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

class PortPinArrowMixin:
    # class variables
    _ARROW_CLASS = Arrow

    # instance attributes
    _brect  : QRectF
    _hshape : QPainterPath
    _node   : Node
    _arrow  : Arrow

    def initArrow(self : Self) -> None:
        self._arrow = self._ARROW_CLASS(self)
        self._arrow.setDirection(self._direction)

    def initAnchorPoints(self : Self) -> None:
        BasePortPin.initAnchorPoints(self)
        self._anchor_points["Name"].setPos(
            PortArrow._SIZE + self._NAME_OFFSET, 0
        )

    def onGeometryChange(self : Self) -> None:
        self.prepareGeometryChange()
        node_rect = self._node._brect
        node_rect.translate(self._node.pos())
        arrow_rect = self._arrow._brect
        arrow_rect.translate(self._arrow.pos())
        self._brect = node_rect | arrow_rect
        self._hshape.clear()
        self._hshape.addRect(self._brect)

    def onSelectionChange(self : Self, selected : bool) -> None:
        BasePortPin.onSelectionChange(self, selected)
        self._arrow.setSelected(selected)

    def onSettingsChange(self : Self) -> None:
        self._arrow.onSettingsChange()

    def onDirectionChange(self : Self, direction : SignalDirection) -> None:
        self._arrow.setDirection(direction)

class PortNode(Node):
    pass

class PortArrow(Arrow):
    _PATH_IN  = Arrow._PATH_TOWARDS
    _PATH_OUT = Arrow._PATH_AWAY

class PortName(PortPinText):
    pass

class PortComment(PortPinText):
    pass

class Port(ElementPosMixin, PortPinArrowMixin, BasePortPin):
    # class attributes
    _NODE_CLASS    = PortNode
    _ARROW_CLASS   = PortArrow
    _NAME_CLASS    = PortName
    _COMMENT_CLASS = PortComment
    _PROPERTY_SPECS = \
        ElementPosMixin._PROPERTY_SPECS_POS | \
        BasePortPin._PROPERTY_SPECS

    # instance attributes
    _node  : PortNode
    _arrow : PortArrow

    def __init__(self : Self, pos : Optional[QPointF] = None) -> None:
        BasePortPin.__init__(self)
        if pos is not None:
            self.setPos(pos)
        self.initArrow()
        self.onGeometryChange()

    @classmethod
    def createOrUpdate(
        cls       : Self,
        *,
        name      : str                       = "",
        direction : Optional[SignalDirection] = None,
        range     : Optional[VectorRange]     = None,
        pos       : Optional[QPointF]         = None,
        inst      : Optional[Self]            = None
    ) -> "Port":
        inst : Port = cls() if inst is None else inst
        if name is not None:
            inst.name = name
        if direction is not None:
            inst.direction = direction
        if range is not None:
            inst.range = range
        if pos is not None:
            inst.setPos(pos)
        return inst

    def ctxMenuEdit(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        view.editPort(self)

class BasePin(ElementLocMixin, BasePortPin):
    # class attributes
    _PROPERTY_SPECS = \
        ElementLocMixin._PROPERTY_SPECS_LOC | \
        BasePortPin._PROPERTY_SPECS

    # instance attributes
    _loc : EdgeLoc

    def getLoc(self : Self) -> EdgeLoc:
        return self._loc

    @classmethod
    def createOrUpdate(
        cls       : Self,
        *,
        name      : str                       = "",
        direction : Optional[SignalDirection] = None,
        range     : Optional[VectorRange]     = None,
        loc       : Optional[EdgeLoc]         = None,
        parent    : Optional["PinRect"]       = None,
        inst      : Optional[Self]            = None
    ) -> "BasePin":
        inst : BasePin = cls() if inst is None else inst
        if name is not None:
            inst.name = name
        if direction is not None:
            inst.direction = direction
        if range is not None:
            inst.range = range
        if loc is not None:
            inst.setLoc(loc)
        if parent is not None:
            inst.setParentItem(parent)
        return inst

class BlockPinNode(Node):
    pass

class BlockPinArrow(Arrow):
    _PATH_IN  = Arrow._PATH_AWAY
    _PATH_OUT = Arrow._PATH_TOWARDS

class BlockPinName(PortPinText):
    pass

class BlockPinComment(PortPinText):
    pass

class BlockPin(PortPinArrowMixin, BasePin):
    # class attributes
    _NODE_CLASS    = BlockPinNode
    _ARROW_CLASS   = BlockPinArrow
    _NAME_CLASS    = BlockPinName
    _COMMENT_CLASS = BlockPinComment

    # instance attributes
    _node  : BlockPinNode
    _arrow : BlockPinArrow

    def __init__(self : Self, parent : Optional["Block"] = None) -> None:
        BasePortPin.__init__(self)
        self.setParentItem(parent)
        self.initArrow()
        self.onGeometryChange()

    @classmethod
    def createOrUpdate(
        cls       : Self,
        *,
        name      : str                       = "",
        direction : Optional[SignalDirection] = None,
        range     : Optional[VectorRange]     = None,
        loc       : Optional[EdgeLoc]         = None,
        parent    : Optional["Block"]         = None,
        inst      : Optional[Self]            = None
    ) -> "BlockPin":
        return super().createOrUpdate(
            name      = name,
            direction = direction,
            range     = range,
            loc       = loc,
            parent    = parent,
            inst      = inst
        )

    def ctxMenuEdit(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        view.editBlockPin(self)
