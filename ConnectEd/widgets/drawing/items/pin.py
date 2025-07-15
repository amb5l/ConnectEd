__all__ = ["BlockPin", "cmdPlaceBlockPin"]

from typing import Self, Optional

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem
from PyQt6.QtGui     import QPainter, QPainterPath

from .. import KP, Edge, EdgeLoc, SignalDirection, VectorRange, \
               CustomGraphicsItem, ElementMixin, cmdPlaceElement, Block

from .base_text import BaseText
from .base_rect import BaseRectWithPins

from . import LinePref, FillPref

from .... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingScene


class PinText(BaseText):
    """Text for display of pin name/number."""
    _attr  : str
    _value : str

    def __init__(
        self   : Self,
        attr   : str,      # parent attribute name e.g. "name" for pin name
        pos    : QPointF,  # offset from pin position (unrotated)
        anchor : KP,
        parent : "Pin"
    ) -> None:
        super().__init__("", pos, anchor)
        self.setParentItem(parent)
        self._attr = attr
        self.onTextChanged(attr, getattr(parent, attr))
        parent._esm.textChanged.connect(self.onTextChanged)

    def onTextChanged(self : Self, attr : str, value : str) -> None:
        if attr == self._attr:
            self._value = value
            super().setText(value)

class Pin(CustomGraphicsItem, ElementMixin):
    # class attributes
    _SIZE           = 4
    _PIN_NAME_CLASS = None  # subclass to override
    _PIN_NAME_POS   = None    # subclass to override

    # instance attributes
    _loc       : EdgeLoc
    _name      : str
    _direction : SignalDirection
    _range     : Optional[VectorRange]
    _name_text : PinText
    _rect      : QRectF
    _shape     : QPainterPath
    _path_open : QPainterPath
    _path_nc   : QPainterPath

    def __init__(
        self      : Self,
        name      : str,
        direction : SignalDirection,
        range     : Optional[VectorRange],
        parent    : BaseRectWithPins,
        loc       : EdgeLoc
    ) -> None:
        CustomGraphicsItem.__init__(self, parent)
        ElementMixin.initElement(self, line=LinePref(), fill=FillPref())
        self.setLoc(loc)
        self._name = "?"
        self._direction = direction
        self._range = range
        self._name_text = self._PIN_NAME_CLASS(
            "name", self._PIN_NAME_POS, KP.CENTER_LEFT, self
        )
        self._shape = QPainterPath()
        self.name = name # recalculates self._rect
        s = self._SIZE / 2
        self._path_open = QPainterPath()
        self._path_open.addRect(QRectF(-s, -s, 2*s, 2*s))
        self._path_nc = QPainterPath()
        self._path_nc.moveTo(-s, +s)
        self._path_nc.lineTo(+s, -s)
        self._path_nc.moveTo(+s, +s)
        self._path_nc.lineTo(-s, -s)

    def onSettingsChange(self : Self) -> None:
        self.refresh()
        super().onSettingsChange()

    def setLoc(self : Self, loc : EdgeLoc) -> None:
        self._loc = loc
        match loc.edge:
            case Edge.LEFT:   self.setRotation(0)
            case Edge.RIGHT:  self.setRotation(180)
            case Edge.TOP:    self.setRotation(90)
            case Edge.BOTTOM: self.setRotation(270)
        parent : BaseRectWithPins = self.parentItem()
        super().setPos(parent.getEdgeLocPos(loc))

    def setLocPos(
        self : Self,
        pos  : QPointF,
        snap : Optional[QPointF] = None
    ) -> None:
        parent : BaseRectWithPins = self.parentItem()
        self.setLoc(parent.getEdgeLoc(pos, snap))

    @property
    def name(self : Self) -> str:
        return self._name

    @name.setter
    def name(self : Self, name : str) -> None:
        self._name = name
        self._esm.textChanged.emit("name", name)
        self.refresh()

    @property
    def direction(self : Self) -> SignalDirection:
        return self._direction

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
        self._rect = QRectF(-s, -s, 2*s, 2*s)
        self._rect |= self._name_text.boundingRect()
        self._shape.clear()
        self._shape.addRect(self._rect)

class BlockPinName(PinText):
    pass

class BlockPinDirection(CustomGraphicsItem, ElementMixin):
    """Pin direction indicator for block pins."""
    _RECT     = QRectF(0, -5, 10, 10)
    _PATH_IN  = [(8,0), (4,-4), (0,-4), (0,4), (4,4)]
    _PATH_OUT = [(0,0), (4,-4), (8,-4), (8,4), (4,4)]
    _PATH_BI  = [(0,0), (4,-4), (8,0), (4,4)]

    _shape    : QPainterPath
    _path_in  : QPainterPath
    _path_out : QPainterPath
    _path_bi  : QPainterPath
    _path     : QPainterPath

    def __init__(self : Self, parent : Pin) -> None:
        CustomGraphicsItem.__init__(self, parent)
        ElementMixin.initElement(self, line=LinePref(), fill=FillPref())
        self._shape = QPainterPath()
        self._shape.addRect(self._RECT)
        self._path_in = self._buildPath(self._PATH_IN)
        self._path_out = self._buildPath(self._PATH_OUT)
        self._path_bi = self._buildPath(self._PATH_BI)
        self.updateDirection(parent.direction)
        parent._esm.directionChanged.connect(self.updateDirection)

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
        return self._RECT

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

class BlockPin(Pin):
    _PIN_NAME_CLASS = BlockPinName
    _PIN_NAME_POS   = QPointF(10, 0)

    _indicator : BlockPinDirection

    def __init__(
        self      : Self,
        name      : str,
        direction : SignalDirection,
        range     : Optional[VectorRange],
        block     : Block,
        loc       : EdgeLoc
    ) -> None:
        super().__init__(name, direction, range, block, loc)
        self._indicator = BlockPinDirection(self)
        block._esm.sizeChanged.connect(self.onBlockSizeChanged)
        hub.settings.change.connect(self.onSettingsChange)

    def onBlockSizeChanged(self : Self) -> None:
        # unplace if edge becomes too short
        pass

class cmdPlaceBlockPin(cmdPlaceElement):
    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        element : BlockPin,
        parent  : Block
    ):
        super().__init__(scene, element)

    def redo(self : Self) -> None:
        super().redo()