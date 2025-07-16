__all__ = ["BlockPin", "cmdPlaceBlockPin"]

from typing import Self, Optional

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, \
                            QGraphicsItemGroup, QStyle
from PyQt6.QtGui     import QPainter, QPainterPath, QPen, QBrush, QFontMetrics

from .. import KP, Edge, EdgeLoc, SignalDirection, VectorRange, TextPref, \
               CustomGraphicsItem, CustomGraphicsSimpleTextItem, \
               ElementMixin, Block, cmdPlaceElement

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
        self.update()

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

class PinName(CustomGraphicsSimpleTextItem, ElementMixin):
    _pos           : QPointF
    _tight_rect    : QRectF
    _anchor_offset : QPointF

    def __init__(
        self   : Self,
        text   : str = "",
        pos    : QPointF = QPointF(0, 0),
        parent : Optional["Pin"] = None
    ) -> None:
        CustomGraphicsSimpleTextItem.__init__(self, text, parent)
        self.initElement(line=None, fill=None, text=TextPref(), bare=True)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable , True)
        self._pos = pos
        self.refresh()

    def setPos(self : Self, pos : QPointF) -> None:
        self._pos = pos
        super().setPos(pos - self._anchor_offset)

    def pos(self : Self) -> QPointF:
        return self._pos

    def setText(self : Self, text : str) -> None:
        super().setText(text)
        self.refresh()

    def tightBoundingRect(self : Self) -> QRectF:
        return self._tight_rect

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setBrush(QBrush(self.appearance.text.current))
        option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.setPen(self.appearance.outline.pen)
            painter.drawRect(self._tight_rect)

    def refresh(self : Self) -> None:
        if not self.text():
            self._tight_rect = QRectF()
            return
        font = self.font()
        metrics = QFontMetrics(font)
        baseline_tight_rect = metrics.tightBoundingRect(self.text())
        baseline_y = metrics.ascent()
        self._tight_rect = baseline_tight_rect.translated(0, baseline_y)
        self._anchor_offset = QPointF(0, self.boundingRect().height() / 2)
        self.setPos(self._pos)

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
    _rect       : QRectF
    _shape      : QPainterPath

    def __init__(
        self      : Self,
        name      : str,
        direction : SignalDirection,
        range     : Optional[VectorRange],
        loc       : EdgeLoc,
        parent    : BaseRectWithPins,
        finish    : bool = True
    ) -> None:
        super().__init__(parent)
        self.setPos(-parent.pos())
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self._rect = QRectF()
        self._shape = QPainterPath()
        self._name = name
        self._direction = direction
        self._range = range
        self._entry = self._ENTRY_CLASS(self)
        self.addToGroup(self._entry)
        self._name_text = self._NAME_CLASS(name, QPointF(), self)
        self.addToGroup(self._name_text)
        if finish:
            self.refresh()
            self.setLoc(loc)
        parent._esm.sizeChanged.connect(self.onParentSizeChanged)

    def onSettingsChange(self : Self) -> None:
        super().onSettingsChange()
        self.refresh()
        self.update()

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
        parent : BaseRectWithPins = self.parentItem()
        edge_pos = parent.getEdgeLocPos(loc)
        self.setPos(edge_pos)

    def setLocPos(
        self : Self,
        pos  : QPointF,
        snap : Optional[QPointF] = None
    ) -> None:
        parent : BaseRectWithPins = self.parentItem()
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
            painter.setPen(self._entry.appearance.outline.pen)
            painter.drawRect(self._rect)

    def refresh(self : Self) -> None:
        self.prepareGeometryChange()
        self._name_text.setPos(self._namePos())
        entry_rect = self._entryRect()
        name_rect = self._nameRect()
        other_rect = self._otherRect()
        self._rect = entry_rect | name_rect | other_rect
        self._shape.clear()
        self._shape.addRect(self._rect)

    def _entryRect(self : Self) -> QRectF:
        rect = self._entry.boundingRect()
        rect.translate(self._entry.pos())
        return rect

    def _nameRect(self : Self) -> QRectF:
        rect = QRectF(self._name_text.tightBoundingRect())
        actual_pos = self._name_text.pos() - self._name_text._anchor_offset
        rect.translate(actual_pos)
        return rect

    def _otherRect(self : Self) -> QRectF:
        return QRectF()

    def _namePos(self : Self) -> QPointF:
        parent : BaseRectWithPins = self.parentItem()
        parent_edge_width = parent.appearance.line.pen.width()
        name_offset = parent_edge_width + self._NAME_GAP
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
        self.refresh()
        self.update()

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
        super().__init__(name, direction, range, loc, block, finish=False)
        self._indicator = BlockPinDirection(self)
        self.addToGroup(self._indicator)
        self.setLoc(loc)
        self.refresh()
        block._esm.directionChanged.connect(self._indicator.updateDirection)

    def _namePos(self : Self) -> QPointF:
        indicator_width = self._indicator._rect.width()
        name_offset = indicator_width + self._NAME_GAP
        return QPointF(name_offset, 0)

    def _otherRect(self : Self) -> QRectF:
        rect = self._indicator.boundingRect()
        rect.translate(self._indicator.pos())
        return rect

class cmdPlaceBlockPin(cmdPlaceElement):
    pass
