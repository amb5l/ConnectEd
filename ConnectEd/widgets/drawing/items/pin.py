__all__ = ["BlockPin", "cmdPlaceBlockPin"]

from typing import Self, Optional, Any

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, \
                            QGraphicsItemGroup, QStyle
from PyQt6.QtGui     import QPainter, QPainterPath

from . import Edge, EdgeLoc, SignalDirection, VectorRange, \
              CustomGraphicsItem, cmdPlaceElement

from .node       import Node
from .annotation import Annotation
from .arrow      import SignalArrow

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .base_rect  import BaseRectWithPins

from .... import hub


class BasePin(QGraphicsItemGroup):
    # class attributes
    _NODE_CLASS  = None  # subclass to override
    _INNER_CLASS = None  # subclass to override
    _OUTER_CLASS = None  # subclass to override
    _NAME_CLASS  = None  # subclass to override
    _NAME_GAP    = 2

    # instance attributes
    _name       : str
    _direction  : SignalDirection
    _range      : Optional[VectorRange]
    _loc        : EdgeLoc
    _node       : Node
    _inner      : Optional[CustomGraphicsItem]
    _outer      : Optional[CustomGraphicsItem]
    _name_text  : Annotation
    _rect       : QRectF
    _shape      : QPainterPath

    def __init__(
        self      : Self,
        name      : str,
        direction : SignalDirection,
        range     : Optional[VectorRange],
        loc       : EdgeLoc,
        parent    : "BaseRectWithPins"
    ) -> None:
        super().__init__(parent)
        self.setPos(-parent.pos())
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self._node = self._NODE_CLASS(self)
        self.addToGroup(self._node)
        if self._INNER_CLASS is not None:
            self._inner = self._INNER_CLASS(self)
            self.addToGroup(self._inner)
        if self._OUTER_CLASS is not None:
            self._outer = self._OUTER_CLASS(self)
            self.addToGroup(self._outer)
        self._name_text = self._NAME_CLASS(name, QPointF(), self)
        self.addToGroup(self._name_text)
        self._rect = QRectF()
        self._shape = QPainterPath()
        self.name = name
        self.direction = direction
        self.range = range
        self.refresh()
        self.setLoc(loc)
        hub.settings.changed.connect(self.onSettingsChange)

    def itemChange(
        self   : Self,
        change : QGraphicsItemGroup.GraphicsItemChange,
        value  : Any
    ) -> Any:
        if change == self.GraphicsItemChange.ItemSelectedHasChanged:
            self.onSelectionChange(value)
        return super().itemChange(change, value)

    def onSettingsChange(self : Self) -> None:
        self.refresh()
        self.update()

    def onSelectionChange(self : Self, selected : bool) -> None:
        self._node.onSelectionChange(selected)
        self._name_text.onSelectionChange(selected)
        if hasattr(self, "_inner"):
            self._inner.onSelectionChange(selected)
        if hasattr(self, "_outer"):
            self._outer.onSelectionChange(selected)

    def onParentSizeChanged(self : Self) -> None:
        # TODO: unplace if edge becomes too short
        pass

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
        parent : "BaseRectWithPins" = self.parentItem()
        edge_pos = parent.getEdgeLocPos(loc)
        self.setPos(edge_pos)

    def setLocPos(
        self : Self,
        pos  : QPointF,
        snap : Optional[QPointF] = None
    ) -> None:
        parent : "BaseRectWithPins" = self.parentItem()
        self.setLoc(parent.getEdgeLoc(pos, snap))

    def boundingRect(self : Self) -> QRectF:
        return self._rect

    def shape(self : Self) -> QPainterPath:
        return self._shape

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : Optional[QWidget] = None
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.setPen(self._node.appearance.outline.pen)
            painter.drawRect(self._rect)

    def refresh(self : Self) -> None:
        self.prepareGeometryChange()
        self._node.setPos(self._entryPos())
        self._name_text.setPos(self._namePos())
        self._rect = self._nodeRect() | self._nameRect()
        self._rect |= self._innerRect() | self._outerRect()
        self._shape.clear()
        self._shape.addRect(self._rect)

    def _nodeRect(self : Self) -> QRectF:
        rect = self._node.boundingRect()
        rect.translate(self._node.pos())
        return rect

    def _nameRect(self : Self) -> QRectF:
        rect = QRectF(self._name_text.tightBoundingRect())
        rect.translate(self._name_text.pos() - self._name_text._anchor_offset)
        return rect

    def _innerRect(self : Self) -> QRectF:
        if hasattr(self, "_inner"):
            return self._inner.boundingRect()
        return QRectF()

    def _outerRect(self : Self) -> QRectF:
        if hasattr(self, "_outer"):
            return self._outer.boundingRect()
        return QRectF()

    def _entryPos(self : Self) -> QPointF:
        if hasattr(self, "_outer"):
            return QPointF(self._outer._SIZE, 0)
        return QPointF(0, 0)

    def _namePos(self : Self) -> QPointF:
        parent : "BaseRectWithPins" = self.parentItem()
        parent_edge_width = parent.appearance.line.pen.width()
        name_offset = parent_edge_width + self._NAME_GAP
        if hasattr(self, "_inner"):
            name_offset += self._inner._SIZE
        return QPointF(name_offset, 0)

    @property
    def name(self : Self) -> str:
        return self._name

    @name.setter
    def name(self : Self, name : str) -> None:
        self._name = name
        self.prepareGeometryChange()
        self._name_text.setText(name)

    @property
    def direction(self : Self) -> SignalDirection:
        return self._direction

    @direction.setter
    def direction(self : Self, direction : SignalDirection) -> None:
        self._direction = direction

    @property
    def range(self : Self) -> Optional[VectorRange]:
        return self._range

    @range.setter
    def range(self : Self, range : Optional[VectorRange]) -> None:
        self._range = range

class BlockPinNode(Node):
    pass

class BlockPinName(Annotation):
    pass

class BlockPinArrow(SignalArrow):
    _PATH_IN  = SignalArrow._PATH_AWAY
    _PATH_OUT = SignalArrow._PATH_TOWARDS

class BlockPin(BasePin):
    _NODE_CLASS  = BlockPinNode
    _INNER_CLASS = BlockPinArrow
    _NAME_CLASS  = BlockPinName

    _inner : BlockPinArrow

    @property
    def direction(self : Self) -> SignalDirection:
        return self._direction

    @direction.setter
    def direction(self : Self, direction : SignalDirection) -> None:
        self._direction = direction
        self._inner.updateDirection(direction)
        self.update()

class cmdPlaceBlockPin(cmdPlaceElement):
    pass
