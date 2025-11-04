from typing import Self
from enum   import Enum

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsPathItem

from ....core.defs import PITCH

from ..properties import PropertySpec

from . import SignalDirection

from .port_pin import PortPinMixin, PortPinText
from .entry    import Entry

from .mixin.paint  import ItemPaintMixin
from .mixin.change import ItemChangeMixin
from .mixin.line   import ItemLineMixin
from .mixin.fill   import ItemFillMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene


# documentation - DO NOT CHANGE
_PIN_DOT_SIZE   = 2
_PIN_CLK_SIZE   = 3
_EXT_ARROW_SIZE = 3
_INT_ARROW_SIZE = 6


class BasePinArrow(
    ItemPaintMixin,
    ItemChangeMixin,
    ItemLineMixin,
    ItemFillMixin,
    QGraphicsPathItem
):
    # instance attributes
    _direction : SignalDirection

    def __init__(self : Self, parent : QGraphicsItem | None = None) -> None:
        QGraphicsPathItem.__init__(self, parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.initLine()
        self.initFill()
        self._direction = SignalDirection.BI

    def onSceneChange(self : Self, scene : "DrawingScene") -> None:
        self._setPath(scene)

    def onSelectionChange(self : Self, selected : bool) -> None:
        parent = self.parentItem()
        if parent and parent.isSelected() != selected:
            parent.setSelected(selected)

    @property
    def direction(self : Self) -> SignalDirection:
        return self._direction

    @direction.setter
    def direction(self : Self, value : SignalDirection) -> None:
        self._direction = value
        self._setPath()

    def _setPath(self : Self, scene : "DrawingScene | None" = None) -> None:
        if scene is None:
            if (scene := self.scene()) is None:
                return
        if hasattr(scene, 'paths') \
        and self.__class__.__name__ in scene.paths \
        and self._direction.value in scene.paths[self.__class__.__name__]:
            path = scene.paths[self.__class__.__name__][self._direction.value]
            self.setPath(path)


class BasePinEntry(Entry):
    pass


class BasePinName(PortPinText):
    pass


class BasePinComment(PortPinText):
    pass


class BasePin(ItemPaintMixin, PortPinMixin, QGraphicsPathItem):
    @classmethod
    def _getArrowClass(cls) -> type[BasePinArrow]:
        raise NotImplementedError("Subclasses must implement this method")

    @classmethod
    def _getEntryClass(cls) -> type[BasePinEntry]:
        raise NotImplementedError("Subclasses must implement this method")

    @classmethod
    def _getNameClass(cls) -> type[BasePinName]:
        raise NotImplementedError("Subclasses must implement this method")

    @classmethod
    def _getCommentClass(cls) -> type[BasePinComment]:
        raise NotImplementedError("Subclasses must implement this method")

    # instance attributes
    _arrow : BasePinArrow

    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None,
        bare   : bool = False
    ) -> None:
        QGraphicsPathItem.__init__(self, parent)
        self.initPortPin(bare)
        self._setPath()
        self._entry.setPos(-PITCH, 0)
        self._arrow = self._getArrowClass()(self)

    @property
    def direction(self : Self) -> SignalDirection:
        return super().direction

    @direction.setter
    def direction(self : Self, value : SignalDirection) -> None:
        super(BasePin, BasePin).direction.__set__(self, value)
        self._arrow.direction = value

    def onGeometryChange(self : Self) -> None:
        pass

    def onSceneChange(self : Self, scene : "DrawingScene") -> None:
        self._arrow.direction = self._direction
        self._setPath(scene)

    def onSelectionChange(self : Self, selected : bool) -> None:
        self._arrow.setSelected(selected)
        self._entry.setSelected(selected)

    def _setPath(self : Self, scene : "DrawingScene | None" = None) -> None:
        raise NotImplementedError("Subclasses must implement this method")


class BasePinDotMixin:
    _PROPERTY_SPECS_DOT = {
        "Dot" : PropertySpec(
            type_name = "bool",
            getter    = lambda self: self._dot,
            setter    = lambda self, value: setattr(self, '_dot', value)
        )
    }

    # instance attributes
    _dot : bool = False

    @property
    def dot(self : Self) -> bool:
        return self._dot

    @dot.setter
    def dot(self : Self, value : bool) -> None:
        self._dot = value


class BasePinClockMixin:
    _PROPERTY_SPECS_CLOCK = {
        "Clock" : PropertySpec(
            type_name = "bool",
            getter    = lambda self: self._clock,
            setter    = lambda self, value: setattr(self, '_clock', value)
        )
    }

    # instance attributes
    _clock : bool = False

    @property
    def clock(self : Self) -> bool:
        return self._clock

    @clock.setter
    def clock(self : Self, value : bool) -> None:
        self._clock = value
        self.onPropertyChange()
