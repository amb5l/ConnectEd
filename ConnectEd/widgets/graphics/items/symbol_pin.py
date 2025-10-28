from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from ..properties import PropertySpec

from .mixin.pos  import ItemPosMixin
from .mixin.line import ItemLineMixin

from .port_pin import PortPinText, PortPinMixin
from .base_pin import BasePinArrow, BasePin, _PIN_CLK_SIZE
from .entry    import Entry

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene


class SymbolPinArrow(BasePinArrow):
    pass


class SymbolPinEntry(Entry):
    pass


class SymbolPinName(PortPinText):
    pass


class SymbolPinComment(PortPinText):
    pass


class SymbolPin(ItemPosMixin, BasePin):
    # class attributes
    _PROPERTY_SPECS = \
        ItemPosMixin._PROPERTY_SPECS_POS | \
        PortPinMixin._PROPERTY_SPECS_NAME | \
        {
            "Dot" : PropertySpec(
                type_name = "bool",
                getter    = lambda self: self._dot,
                setter    = lambda self, value: setattr(self, '_dot', value)
            ),
            "Clock" : PropertySpec(
                type_name = "bool",
                getter    = lambda self: self._clock,
                setter    = lambda self, value: setattr(self, '_clock', value)
            )
        } | \
        PortPinMixin._PROPERTY_SPECS_PORT_PIN | \
        ItemLineMixin._PROPERTY_SPECS_LINE

    @classmethod
    def _getArrowClass(cls) -> type[SymbolPinArrow]:
        return SymbolPinArrow

    @classmethod
    def _getEntryClass(cls) -> type[SymbolPinEntry]:
        return SymbolPinEntry

    @classmethod
    def _getNameClass(cls) -> type[SymbolPinName]:
        return SymbolPinName

    @classmethod
    def _getCommentClass(cls) -> type[SymbolPinComment]:
        return SymbolPinComment

    # instance attributes
    _dot   : bool
    _clock : bool

    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None,
        bare   : bool = False
    ) -> None:
        self._dot   = True
        self._clock = True
        super().__init__(parent, bare)

    @property
    def dot(self : Self) -> bool:
        return self.getPropertyValue("Dot")

    @dot.setter
    def dot(self : Self, value : bool) -> None:
        self.setPropertyValue("Dot", value)
        self._setPath()

    @property
    def clock(self : Self) -> bool:
        return self.getPropertyValue("Clock")

    @clock.setter
    def clock(self : Self, value : bool) -> None:
        self.setPropertyValue("Clock", value)
        self._setPath()

    def _setPath(self : Self, scene : "DrawingScene | None") -> None:
        if scene is None:
            return
        key = (self._dot, self._clock)
        self.setPath(scene.paths["SymbolPin"][key])
        self._anchor_points["Name"].setPos(QPointF(
            self._AP_NAME_OFFSET + (_PIN_CLK_SIZE if self._clock else 0), 0
        ))
