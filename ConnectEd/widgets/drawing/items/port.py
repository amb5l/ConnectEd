__all__ = ["Port", "cmdPlacePort"]

from typing import Self, Optional, Any

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, \
                            QGraphicsItemGroup, QStyle
from PyQt6.QtGui     import QPainter, QPainterPath

from . import SignalDirection, VectorRange, cmdPlaceElement

from .node       import Node
from .annotation import Annotation
from .arrow      import SignalArrow

from .... import hub


class PortNode(Node):
    pass

class PortName(Annotation):
    pass

class PortArrow(SignalArrow):
    _PATH_IN  = SignalArrow._PATH_TOWARDS
    _PATH_OUT = SignalArrow._PATH_AWAY

class Port(QGraphicsItemGroup):
    # class attributes
    _NAME_GAP    = 2

    # instance attributes
    _name      : str
    _direction : SignalDirection
    _range     : Optional[VectorRange]
    _node      : PortNode
    _arrow     : PortArrow
    _name_text : Annotation
    _rect      : QRectF
    _shape     : QPainterPath

    def __init__(
        self      : Self,
        name      : str                   = "",
        direction : SignalDirection       = SignalDirection.IN,
        range     : Optional[VectorRange] = None,
        pos       : QPointF               = QPointF()
    ) -> None:
        super().__init__()
        self.setPos(pos)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self._node = PortNode(self)
        self.addToGroup(self._node)
        self._arrow = PortArrow(self)
        self.addToGroup(self._arrow)
        self._name_text = PortName(name, QPointF(), self)
        self.addToGroup(self._name_text)
        self._rect = QRectF()
        self._shape = QPainterPath()
        self.name = name
        self.direction = direction
        self.range = range
        self.onSettingsChange()
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
        self.onGeometryChange()

    def onGeometryChange(self : Self) -> None:
        self.prepareGeometryChange()
        self._node.setPos(QPointF(0, 0))
        self._name_text.setPos(self._namePos())
        self._rect = self._nodeRect() | self._nameRect() | self._arrowRect()
        self._shape.clear()
        self._shape.addRect(self._rect)

    def onSelectionChange(self : Self, selected : bool) -> None:
        self._node.onSelectionChange(selected)
        self._arrow.onSelectionChange(selected)
        self._name_text.onSelectionChange(selected)

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

    def _nodeRect(self : Self) -> QRectF:
        rect = self._node.boundingRect()
        rect.translate(self._node.pos())
        return rect

    def _nameRect(self : Self) -> QRectF:
        rect = QRectF(self._name_text.tightBoundingRect())
        rect.translate(self._name_text.pos() - self._name_text._anchor_offset)
        return rect

    def _arrowRect(self : Self) -> QRectF:
        return self._arrow.boundingRect()

    def _namePos(self : Self) -> QPointF:
        name_offset = self._arrow._SIZE + self._NAME_GAP
        return QPointF(name_offset, 0)

    @property
    def name(self : Self) -> str:
        return self._name

    @name.setter
    def name(self : Self, name : str) -> None:
        self._name = name
        self._name_text.setText(name)
        self.onGeometryChange()

    @property
    def direction(self : Self) -> SignalDirection:
        return self._direction

    @direction.setter
    def direction(self : Self, direction : SignalDirection) -> None:
        self._direction = direction
        self._arrow.updateDirection(direction)
        self.update()

    @property
    def range(self : Self) -> Optional[VectorRange]:
        return self._range

    @range.setter
    def range(self : Self, range : Optional[VectorRange]) -> None:
        self._range = range

    @classmethod
    def createOrUpdate(
        cls  : Self,
        *args,
        inst : Optional[Self] = None
    ) -> "Port":
        inst = cls() if inst is None else inst
        for arg in args:
            match arg:
                case str() as name:
                    inst.name = name
                case SignalDirection() as direction:
                    inst.direction = direction
                case VectorRange() as range:
                    inst.range = range
                case QPointF() as pos:
                    inst.setPos(pos)
                case None:
                    pass
                case _:
                    raise TypeError(f"Unsupported argument type: {type(arg)}")
        return inst

class cmdPlacePort(cmdPlaceElement):
    pass
