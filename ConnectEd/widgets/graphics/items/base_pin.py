from typing import Self

from PyQt6.QtWidgets import QGraphicsItem, QGraphicsPathItem

from ....core.defs  import PITCH
from ....core.types import Direction, DataKind

from ..properties import InherentProperty

from .port_pin import PortPinMixin

from .mixin            import ItemSettingsMixin
from .mixin.paint      import ItemPaintMixin
from .mixin.line       import ItemLineMixin
from .mixin.fill       import ItemFillMixin
from .mixin.change     import ItemChangeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene


# documentation - DO NOT CHANGE
_PIN_SIZE       = PITCH
_PIN_DOT_SIZE   = 3
_PIN_CLK_SIZE   = 3
_EXT_ARROW_SIZE = 3
_INT_ARROW_SIZE = 6


class BasePinArrowItem(
    ItemSettingsMixin,
    ItemPaintMixin,
    ItemLineMixin,
    ItemFillMixin,
    ItemChangeMixin,
    QGraphicsPathItem
):
    # instance attributes
    _direction : Direction

    def __init__(self : Self, parent : QGraphicsItem | None = None) -> None:
        QGraphicsPathItem.__init__(self, parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.initChange()
        self.initLine()
        self.initFill()
        self._direction = Direction.BI

    def onSceneChange(self : Self, scene : "DrawingScene") -> None:
        self._setPath(scene)

    def onSelectionChange(self : Self, selected : bool) -> None:
        parent = self.parentItem()
        if parent and parent.isSelected() != selected:
            parent.setSelected(selected)

    def direction(self : Self) -> Direction:
        return self._direction

    def setDirection(self : Self, value : Direction) -> None:
        self._direction = value
        self._setPath()

    def _setPath(self : Self, scene : "DrawingScene | None" = None) -> None:
        if scene is None:
            if (scene := self.scene()) is None:
                return
        item_name = self.__class__.__name__.removesuffix("Item")
        self.setPath(scene.resources[item_name][self._direction.value])


class BasePinItem(ItemPaintMixin, PortPinMixin, QGraphicsPathItem):
    # class attributes
    _ARROW_CLASS : type[BasePinArrowItem] | None = None

    # instance attributes
    _arrow : BasePinArrowItem

    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None,
        fresh  : bool = True
    ) -> None:
        QGraphicsPathItem.__init__(self, parent)
        self.initPortPin(fresh)
        self._setPath()
        self._entry.setPos(-PITCH, 0)
        if self._ARROW_CLASS is not None:
            self._arrow = self._ARROW_CLASS(self)
        else:
            self._arrow = None

    def setDirection(self : Self, value : Direction) -> None:
        super().setDirection(value)
        if self._arrow is not None:
            self._arrow.setDirection(value)

    def onSceneChange(self : Self, scene : "DrawingScene") -> None:
        if self._arrow is not None:
            self._arrow.setDirection(self._direction)
        self._setPath(scene)

    def onSelectionChange(self : Self, selected : bool) -> None:
        if self._arrow is not None:
            self._arrow.setSelected(selected)
        self._entry.setSelected(selected)

    def _setPath(self : Self, scene : "DrawingScene | None" = None) -> None:
        raise NotImplementedError("Subclasses must implement this method")


class BasePinDotMixin:
    # class attributes
    _PROPERTIES_DOT = {
        "Dot" : InherentProperty(
            kind   = DataKind.BOOL,
            getter = lambda self: self._dot,
            setter = lambda self, value: setattr(self, "_dot", value)
        )
    }

    # instance attributes
    _dot : bool = False

    def dot(self : Self) -> bool:
        return self._dot

    def setDot(self : Self, value : bool) -> None:
        self._dot = value
        self._setPath()


class BasePinClockMixin:
    # class attributes
    _PROPERTIES_CLOCK = {
        "Clock" : InherentProperty(
            kind   = DataKind.BOOL,
            getter = lambda self: self._clock,
            setter = lambda self, value: setattr(self, "_clock", value)
        )
    }

    # instance attributes
    _clock : bool = False

    def clock(self : Self) -> bool:
        return self._clock

    def setClock(self : Self, value : bool) -> None:
        self._clock = value
        self._setPath()
