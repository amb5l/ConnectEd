__all__ = ["BlockPin", "cmdPlaceBlockPin"]

from typing import Self, Optional

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, \
                            QGraphicsItemGroup
from PyQt6.QtGui     import QPainter, QPainterPath

from .. import KP, Edge, EdgeLoc, SignalDirection, VectorRange, \
               CustomGraphicsItem, ElementMixin, \
               Block, cmdPlaceElement

from .base_text import BaseText
from .base_rect import BaseRectWithPins

from . import LinePref, FillPref


class PinEntry(CustomGraphicsItem, ElementMixin):
    # class attributes
    _SIZE = 4

    # instance attributes
    _loc       : EdgeLoc
    _rect      : QRectF
    _shape     : QPainterPath
    _path_open : QPainterPath
    _path_nc   : QPainterPath

    def __init__(
        self   : Self,
        parent : "Pin"
    ) -> None:
        CustomGraphicsItem.__init__(self, parent)
        ElementMixin.initElement(self, line=LinePref(), fill=FillPref())
        self._rect = QRectF()
        self._shape = QPainterPath()
        s = self._SIZE / 2
        self._path_open = QPainterPath()
        self._path_open.addRect(QRectF(-s, -s, 2*s, 2*s))
        self._path_nc = QPainterPath()
        self._path_nc.moveTo(-s, +s)
        self._path_nc.lineTo(+s, -s)
        self._path_nc.moveTo(+s, +s)
        self._path_nc.lineTo(-s, -s)
        self.refresh()

    def onSettingsChange(self : Self) -> None:
        super().onSettingsChange()
        self.refresh()

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
        painter.setPen(self.appearance.line.pen)
        painter.setBrush(self.appearance.fill.brush)
        painter.drawPath(self._path_open)

    def refresh(self : Self) -> None:
        s = (self._SIZE + self.appearance.line.pen.width()) / 2
        self._rect.setRect(-s, -s, 2*s, 2*s)
        self._shape.clear()
        self._shape.addRect(self._rect)

class PinName(BaseText):
    pass

class Pin(QGraphicsItemGroup):
    # class attributes
    _ENTRY_CLASS = None  # subclass to override
    _NAME_CLASS  = None  # subclass to override
    _NAME_GAP    = 2

    # instance attributes
    _name       : str
    _direction  : SignalDirection
    _range      : Optional[VectorRange]
    _loc        : EdgeLoc
    _entry      : PinEntry
    _name_text  : PinName

    def __init__(
        self      : Self,
        name      : str,
        direction : SignalDirection,
        range     : Optional[VectorRange],
        loc       : EdgeLoc,
        parent    : BaseRectWithPins,
        refresh   : bool = True
    ) -> None:
        super().__init__(parent)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self._name = name
        self._direction = direction
        self._range = range
        self._entry = self._ENTRY_CLASS(self)
        self.addToGroup(self._entry)
        self._name_text = self._NAME_CLASS(
            name, QPointF(), KP.CENTER_LEFT, self
        )
        self.addToGroup(self._name_text)
        self.setLoc(loc)
        if refresh:
            self.refresh()
        parent._esm.sizeChanged.connect(self.onParentSizeChanged)

    def onSettingsChange(self : Self) -> None:
        super().onSettingsChange()
        self.refresh()

    def onParentSizeChanged(self : Self) -> None:
        # TODO: unplace if edge becomes too short
        pass

    def setLoc(self : Self, loc : EdgeLoc) -> None:
        self._loc = loc
        name_centre = QPointF(self._name_text.boundingRect().center())
        self._name_text.setTransformOriginPoint(name_centre)
        self.prepareGeometryChange()
        match loc.edge:
            case Edge.LEFT:
                self.setRotation(0)
                self._name_text.setRotation(0)
            case Edge.RIGHT:
                self.setRotation(180)
                self._name_text.setRotation(180)
            case Edge.TOP:
                self.setRotation(90)
                self._name_text.setRotation(180)
            case Edge.BOTTOM:
                self.setRotation(270)
                self._name_text.setRotation(0)
        parent : BaseRectWithPins = self.parentItem()
        self.setPos(parent.getEdgeLocPos(loc))

    def setLocPos(
        self : Self,
        pos  : QPointF,
        snap : Optional[QPointF] = None
    ) -> None:
        parent : BaseRectWithPins = self.parentItem()
        self.setLoc(parent.getEdgeLoc(pos, snap))

    def refresh(self : Self) -> None:
        parent : BaseRectWithPins = self.parentItem()
        parent_edge_width = parent.appearance.line.pen.width()
        name_offset = parent_edge_width + self._NAME_GAP
        self.prepareGeometryChange()
        self._name_text.setPos(name_offset, 0)

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

class BlockPinEntry(PinEntry):
    pass

class BlockPinName(PinName):
    pass

class BlockPinDirection(CustomGraphicsItem, ElementMixin):
    """Pin direction indicator for block pins."""
    _SIZE     = 8
    _S        = _SIZE
    _H        = _SIZE/2
    _PATH_IN  = [(_S,0), (_H,-_H), (0,-_H), (0,_H), (_H,_H)]
    _PATH_OUT = [(0,0), (_H,-_H), (_S,-_H), (_S,_H), (_H,_H)]
    _PATH_BI  = [(0,0), (_H,-_H), (_S,0), (_H,_H)]

    _rect     : QRectF
    _shape    : QPainterPath
    _path_in  : QPainterPath
    _path_out : QPainterPath
    _path_bi  : QPainterPath
    _path     : QPainterPath

    def __init__(
        self    : Self,
        parent  : "BlockPin"
    ) -> None:
        CustomGraphicsItem.__init__(self, parent)
        ElementMixin.initElement(self, line=LinePref(), fill=FillPref())
        self._rect = QRectF()
        self._shape = QPainterPath()
        self._path_in = self._buildPath(self._PATH_IN)
        self._path_out = self._buildPath(self._PATH_OUT)
        self._path_bi = self._buildPath(self._PATH_BI)
        self.updateDirection(parent.direction)
        self.refresh()

    def onSettingsChange(self : Self) -> None:
        super().onSettingsChange()
        self._rect.setWidth(self.appearance.line.pen.width())

    def _buildPath(self : Self, points : list[tuple[int, int]]) -> QPainterPath:
        p = QPainterPath()
        p.moveTo(QPointF(*points[0]))
        for point in points[1:]:
            p.lineTo(QPointF(*point))
        p.closeSubpath()
        return p

    def updateDirection(self : Self, direction : SignalDirection) -> None:
        self._direction = direction
        match direction:
            case SignalDirection.IN:
                self._path = self._path_in
            case SignalDirection.OUT:
                self._path = self._path_out
            case SignalDirection.BI:
                self._path = self._path_bi

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
        parent : "Pin" = self.parentItem()
        painter.setPen(self.appearance.line.pen)
        painter.setBrush(self.appearance.fill.brush)
        painter.drawPath(self._path)

    def refresh(self : Self) -> None:
        L = self._SIZE + self.appearance.line.pen.width()
        self._rect.setRect(0, -L/2, L, L)
        self._shape.clear()
        self._shape.addRect(self._rect)

class BlockPin(Pin):
    _ENTRY_CLASS = BlockPinEntry
    _NAME_CLASS  = BlockPinName

    _indicator : BlockPinDirection

    def __init__(
        self      : Self,
        name      : str,
        direction : SignalDirection,
        range     : Optional[VectorRange],
        loc       : EdgeLoc,
        block     : Block
    ) -> None:
        super().__init__(name, direction, range, loc, block, refresh=False)
        self._indicator = BlockPinDirection(self)
        self.addToGroup(self._indicator)
        self.refresh()
        block._esm.directionChanged.connect(self._indicator.updateDirection)

    def refresh(self : Self) -> None:
        # will indicator have handled settings change by now?
        indicator_width = self._indicator._rect.width()
        name_offset = indicator_width + self._NAME_GAP
        self.prepareGeometryChange()
        self._name_text.setPos(QPointF(name_offset, 0))

class cmdPlaceBlockPin(cmdPlaceElement):
    pass
