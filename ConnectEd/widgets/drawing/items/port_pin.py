__all__ = ["Port", "cmdPlacePort", "BlockPin", "cmdPlaceBlockPin"]

from typing import Self, Optional, Any

from PyQt6.QtCore    import QPointF, QRectF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, \
                            QGraphicsItemGroup, QStyle, QGraphicsItem
from PyQt6.QtGui     import QPainter, QPainterPath

from ..properties import PropertySpec, PropertiesMixin

from . import SignalDirection, VectorRange, Edge, EdgeLoc, \
              ElementBoundShapeMixin, \
              ElementChangeMixin, \
              ElementCloneMixin, \
              cmdPlaceElement

from .node import Node
from .arrow import SignalArrow
from .tether_text import TetherText

from .... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .pin_rect import PinRect


class PortPinMixin(ElementBoundShapeMixin, PropertiesMixin):
    # class attributes
    _NODE_CLASS  = None  # subclass to override
    _NAME_CLASS  = None  # subclass to override
    _NAME_OFFSET = 2.5
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
        )
    }

    # instance attributes
    _direction : SignalDirection        # in/out/bi
    _range     : Optional[VectorRange]  # vector range if applicable
    _node      : Node
    _name_text : TetherText
    _brect     : QRectF                 # bounding rect
    _hshape    : QPainterPath           # hit detect shape

    def initPortPin(
        self        : Self,
        name        : str                   = "",
        direction   : SignalDirection       = SignalDirection.IN,
        range       : Optional[VectorRange] = None,
        name_parent : Optional[QGraphicsItem] = None
    ) -> None:
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self.initBoundShape()
        self._node = self._NODE_CLASS(self)
        self.addToGroup(self._node)
        self._name_text = self._NAME_CLASS(
            name,
            QPointF(self._NAME_OFFSET, 0),
            "Center Left"
        )
        self.name = name
        self.direction = direction
        self.range = range
        self.onSettingsChange()
        self.initProperties()
        hub.settings.changed.connect(self.onSettingsChange)

    def onSelectionChange(self : Self, selected : bool) -> None:
        self._node.setSelected(selected)
        self._name_text.setSelected(selected)

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : Optional[QWidget] = None
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.setPen(self._node.outline.pen)
            painter.drawRect(self._brect)

    def _nodeRect(self : Self) -> QRectF:
        rect = self._node._brect
        rect.translate(self._node.pos())
        return rect

    @property
    def name(self : Self) -> str:
        return self._name

    @name.setter
    def name(self : Self, name : str) -> None:
        self.setPropertyValue("Name", name)

    @property
    def range(self : Self) -> Optional[VectorRange]:
        return self._range

    @range.setter
    def range(self : Self, range : Optional[VectorRange]) -> None:
        self._range = range

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        from ....core import toXmlAttrs
        xw.writeStartElement(self.__class__.__name__)
        toXmlAttrs(self, xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr: QXmlStreamReader) -> Self:
        from ....core import fromXmlAttrs
        instance = cls(bare=True)
        fromXmlAttrs(instance, xr)
        return instance

class PortNode(Node):
    pass

class PortArrow(SignalArrow):
    _PATH_IN  = SignalArrow._PATH_AWAY
    _PATH_OUT = SignalArrow._PATH_TOWARDS

class PortName(TetherText):
    pass

class Port(
    ElementChangeMixin,
    PortPinMixin,
    QGraphicsItemGroup
):
    # class attributes
    _NODE_CLASS = PortNode
    _NAME_CLASS = PortName
    _PROPERTY_SPECS = PortPinMixin._PROPERTY_SPECS | {
        "Position X" : PropertySpec(
            type_name = "float",
            getter    = lambda self: self.pos().x(),
            setter    = lambda self, value: self.setPos(QPointF(value, self.pos().y()))
        ),
        "Position Y" : PropertySpec(
            type_name = "float",
            getter    = lambda self: self.pos().y(),
            setter    = lambda self, value: self.setPos(QPointF(self.pos().x(), value))
        )
    }

    # instance attributes
    _arrow : PortArrow

    def __init__(
        self      : Self,
        name      : str                   = "",
        direction : SignalDirection       = SignalDirection.IN,
        range     : Optional[VectorRange] = None,
        pos       : QPointF               = QPointF(),
        bare      : bool                  = False
    ) -> None:
        QGraphicsItemGroup.__init__(self)
        self._arrow = PortArrow(self)
        self._arrow.setDirection(direction)
        self._arrow.setPos(QPointF(self._arrow._SIZE, 0))
        self.addToGroup(self._arrow)
        self.initPortPin(name, direction, range, self._arrow)
        self.setPos(pos)

    def onGeometryChange(self : Self) -> None:
        """Port specific (includes arrow)."""
        self.prepareGeometryChange()
        node_rect = self._node._brect
        node_rect.translate(self._node.pos())
        arrow_rect = self._arrow._brect
        arrow_rect.translate(self._arrow.pos())
        self._brect = node_rect | arrow_rect
        self._hshape.clear()
        self._hshape.addRect(self._brect)

    def onSelectionChange(self : Self, selected : bool) -> None:
        """Port specific (includes arrow)."""
        super().onSelectionChange(selected)
        self._arrow.onSelectionChange(selected)

    @property
    def direction(self : Self) -> SignalDirection:
        return self._direction

    @direction.setter
    def direction(self : Self, direction : SignalDirection) -> None:
        self._direction = direction
        self._arrow.setDirection(direction)
        self.update()

    def _nameRect(self : Self) -> QRectF:
        rect = QRectF(self._name_text.tightBoundingRect())
        name_pos = self._arrow.pos() + self._name_text.pos()
        rect.translate(name_pos - self._name_text._anchor.pos())
        return rect

    @classmethod
    def createOrUpdate(
        cls  : Self,
        name        : Optional[str]             = None,
        direction   : Optional[SignalDirection] = None,
        range       : Optional[VectorRange]     = None,
        pos         : Optional[QPointF]         = None,
        inst        : Optional[Self]            = None
    ) -> Self:
        inst = cls() if inst is None else inst
        if name is not None:
            inst.name = name
        if direction is not None:
            inst.direction = direction
        if range is not None:
            inst.range = range
        if pos is not None:
            inst.setPos(pos)
        return inst

class cmdPlacePort(cmdPlaceElement):
    pass

class BasePin(ElementCloneMixin, PortPinMixin, QGraphicsItemGroup):
    # class attributes
    _INNER_CLASS = None  # subclass to override
    _OUTER_CLASS = None  # subclass to override
    _PROPERTY_SPECS = PortPinMixin._PROPERTY_SPECS | {
        "Location" : PropertySpec(
            type_name = "EdgeLoc",
            getter    = lambda self: self.loc(),
            setter    = lambda self, value: self.setLoc(value)
        )
    }

    # instance attributes
    _loc   : EdgeLoc
    _inner : Optional[QGraphicsItem]
    _outer : Optional[QGraphicsItem]

    def __init__(
        self      : Self,
        name      : str                   = "",
        direction : SignalDirection       = SignalDirection.IN,
        range     : Optional[VectorRange] = None,
        loc       : EdgeLoc               = EdgeLoc(),
        parent    : Optional["PinRect"]   = None,
        bare      : bool                  = False
    ) -> None:
        QGraphicsItemGroup.__init__(self, parent)
        if self._INNER_CLASS is not None:
            self._inner = self._INNER_CLASS(self)
            self._inner.setPos(QPointF(self._inner._SIZE, 0))
            self.addToGroup(self._inner)
        if self._OUTER_CLASS is not None:
            self._outer = self._OUTER_CLASS(self)
            self.addToGroup(self._outer)
        self.initPortPin(
            name, direction, range,
            self._inner if self._INNER_CLASS is not None else None
        )
        self._loc = loc

    def onGeometryChange(self : Self) -> None:
        """Pin specific (includes inner/outer)."""
        self.prepareGeometryChange()
        self._node.setPos(self._nodePos())
        self._name_text.setPos(self._namePos())
        self._brect = self._nodeRect() | self._nameRect()
        self._brect |= self._innerRect() | self._outerRect()
        self._hshape.clear()
        self._hshape.addRect(self._brect)

    def onSelectionChange(self : Self, selected : bool) -> None:
        """Pin specific (includes inner/outer)."""
        super().onSelectionChange(selected)
        if hasattr(self, "_inner"):
            self._inner.onSelectionChange(selected)
        if hasattr(self, "_outer"):
            self._outer.onSelectionChange(selected)

    def itemChange(
        self   : Self,
        change : QGraphicsItemGroup.GraphicsItemChange,
        value  : Any
    ) -> Any:
        result = super().itemChange(change, value)
        if change == QGraphicsItemGroup.GraphicsItemChange.ItemParentHasChanged:
            if value is not None:
                self.setLoc(self._loc)
        return result

    def onParentSizeChanged(self : Self) -> None:
        # TODO: unplace if edge becomes too short
        pass

    def loc(self : Self) -> EdgeLoc:
        return self._loc

    def setLoc(self : Self, loc : EdgeLoc) -> None:
        self._loc = loc
        self.prepareGeometryChange()
        match loc.edge:
            case Edge.LEFT:   self.setRotation(0)
            case Edge.RIGHT:  self.setRotation(180)
            case Edge.TOP:    self.setRotation(90)
            case Edge.BOTTOM: self.setRotation(270)
        if hasattr(self, "_name_text"):
            name_centre = QPointF(self._name_text.boundingRect().center())
            self._name_text.setTransformOriginPoint(name_centre)
            match loc.edge:
                case Edge.LEFT:   self._name_text.setRotation(0)
                case Edge.RIGHT:  self._name_text.setRotation(180)
                case Edge.TOP:    self._name_text.setRotation(180)
                case Edge.BOTTOM: self._name_text.setRotation(0)
        parent : "PinRect" = self.parentItem()
        edge_pos = parent.getEdgeLocPos(loc) if parent else QPointF()
        self.setPos(edge_pos)

    def setLocPos(
        self : Self,
        pos  : QPointF,
        snap : Optional[QPointF] = None
    ) -> None:
        parent : "PinRect" = self.parentItem()
        self.setLoc(parent.getEdgeLoc(pos, snap))

    def _nameRect(self : Self) -> QRectF:
        rect = QRectF(self._name_text.tightBoundingRect())
        name_pos = self._inner.pos() if hasattr(self, "_inner") else QPointF()
        name_pos += self._name_text.pos()
        rect.translate(name_pos - self._name_text._anchor.pos())
        return rect

    def _innerRect(self : Self) -> QRectF:
        return self._inner.boundingRect() if hasattr(self, "_inner") else QRectF()

    def _outerRect(self : Self) -> QRectF:
        if hasattr(self, "_outer"):
            return self._outer.boundingRect()
        return QRectF()

    def _nodePos(self : Self) -> QPointF:
        """Pin specific (includes outer)."""
        if hasattr(self, "_outer"):
            return QPointF(self._outer._SIZE, 0)
        return QPointF(0, 0)

    def _namePos(self : Self) -> QPointF:
        """Pin specific (includes inner/outer)."""
        parent : "PinRect" = self.parentItem()
        name_offset = parent.line.pen.width()/2 + self._NAME_OFFSET
        return QPointF(name_offset, 0)

    def _namePos(self : Self) -> QPointF:
        w = self._inner.line.pen.width() if hasattr(self, "_inner") else 0
        return QPointF(w/2 + self._NAME_GAP, 0)

class BlockPinNode(Node):
    pass

class BlockPinArrow(SignalArrow):
    _PATH_IN  = SignalArrow._PATH_TOWARDS
    _PATH_OUT = SignalArrow._PATH_AWAY

class BlockPinName(TetherText):
    pass

class BlockPin(BasePin):
    _NODE_CLASS  = BlockPinNode
    _NAME_CLASS  = BlockPinName
    _INNER_CLASS = BlockPinArrow

    _inner : BlockPinArrow

    @property
    def direction(self : Self) -> SignalDirection:
        return self._direction

    @direction.setter
    def direction(self : Self, direction : SignalDirection) -> None:
        self._direction = direction
        self._inner.setDirection(direction)
        self.update()

class cmdPlaceBlockPin(cmdPlaceElement):
    pass
