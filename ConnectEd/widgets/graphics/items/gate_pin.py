from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem, QMenu
from PyQt6.QtGui     import QAction

from ....core.defs import PITCH

from .mixin.pos  import ItemPosMixin
from .mixin.line import ItemLineMixin

from .port_pin      import PortPinMixin
from .base_pin      import BasePin, BasePinDotMixin, BasePinClockMixin, _PIN_CLK_SIZE
from .entry         import Entry
from .property_text import PropertyTextSpec

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView
    from ..scenes.drawing import DrawingScene


class GatePinEntry(Entry):
    pass


class GatePin(ItemPosMixin, BasePinDotMixin, BasePinClockMixin, BasePin):
    # class attributes
    _PROPERTY_SPECS = \
        ItemPosMixin._PROPERTY_SPECS_POS | \
        PortPinMixin._PROPERTY_SPECS_NAME | \
        BasePinDotMixin._PROPERTY_SPECS_DOT | \
        BasePinClockMixin._PROPERTY_SPECS_CLOCK | \
        PortPinMixin._PROPERTY_SPECS_PORT_PIN | \
        ItemLineMixin._PROPERTY_SPECS_LINE

    @classmethod
    def _getArrowClass(cls) -> None:
        return None

    @classmethod
    def _getEntryClass(cls) -> type[GatePinEntry]:
        return GatePinEntry

    @classmethod
    def _getPropertyTexts(cls) -> dict[str, PropertyTextSpec]:
        return {}

    # instance attributes
    _length : float

    def __init__(self : Self, parent : QGraphicsItem | None = None) -> None:
        self._length = PITCH
        super().__init__(parent)

    @property
    def inverted(self : Self) -> bool:
        return self._dot

    @inverted.setter
    def inverted(self : Self, value : bool) -> None:
        self._dot = value
        self._setPath()

    def length(self : Self) -> float:
        return self._length

    def setLength(self : Self, length : float) -> None:
        self._length = length

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action(
                "Active Low",
                lambda: view.ui.editSymbolPinDot(self, not self._dot),
                checked=self._dot
            )
        ]

    def _setPath(self : Self, scene : "DrawingScene | None" = None) -> None:
        if scene is None:
            if (scene := self.scene()) is None:
                return
        key = (self._dot, self._clock)
        path = scene.paths["SymbolPin"][key]
        self._anchor_points["Name"].setPos(QPointF(
            self._AP_NAME_OFFSET + (_PIN_CLK_SIZE if self._clock else 0), 0
        ))
        if self._length != PITCH:
            path.setElementPositionAt(0, -self._length, 0)
        self.setPath(path)
