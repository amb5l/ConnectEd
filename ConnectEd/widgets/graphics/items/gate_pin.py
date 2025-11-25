from typing import Self

from PyQt6.QtCore    import QPointF, QXmlStreamWriter
from PyQt6.QtWidgets import QGraphicsItem, QMenu
from PyQt6.QtGui     import QAction, QPainterPath

from ....core.defs import PITCH

from ..property import PropertySpec

from .mixin.pos  import ItemPosMixin
from .mixin.line import ItemLineMixin

from .port_pin      import PortPinMixin
from .base_pin      import BasePin, BasePinDotMixin, BasePinClockMixin, \
                           _PIN_CLK_SIZE

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView
    from ..scenes.drawing import DrawingScene


class GatePin(ItemPosMixin, BasePinDotMixin, BasePinClockMixin, BasePin):
    # class attributes
    _PROPERTY_SPECS = \
        ItemPosMixin._PROPERTY_SPECS_POS | \
        {
            "Name" : PropertySpec(
                getter = lambda self: self._name,
                setter = lambda self, value: setattr(self, "_name", value)
            )
        } | \
        BasePinDotMixin._PROPERTY_SPECS_DOT | \
        BasePinClockMixin._PROPERTY_SPECS_CLOCK | \
        PortPinMixin._PROPERTY_SPECS_PORT_PIN | \
        ItemLineMixin._PROPERTY_SPECS_LINE

    # instance attributes
    _length : float

    def __init__(
        self : Self,
        parent : QGraphicsItem | None = None,
        bare : bool = False  # unused
    ) -> None:
        self._length = PITCH
        super().__init__(parent)

    def inverted(self : Self) -> bool:
        return self._dot

    def setInverted(self : Self, value : bool) -> None:
        self._dot = value
        self._setPath()

    def length(self : Self) -> float:
        return self._length

    def setLength(self : Self, length : float) -> None:
        self._length = length
        self._entry.setPos(-self._length, 0)  # move entry
        self._setPath()  # adjust pin path

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action(
                "Active Low",
                lambda: view.ui.editSymbolPinDot(self, not self._dot),
                checked=self._dot
            )
        ]

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        pass  # exclude from XML

    def _setPath(self : Self, scene : "DrawingScene | None" = None) -> None:
        if scene is None:
            if (scene := self.scene()) is None:
                return
        key = (self._dot, self._clock)
        path = scene.paths["SymbolPin"][key]
        self._handles["Name"].setPos(QPointF(
            self._AP_NAME_OFFSET + (_PIN_CLK_SIZE if self._clock else 0), 0
        ))
        if self._length != PITCH:
            path = QPainterPath(path)  # copy shared path
            path.setElementPositionAt(0, -self._length, 0)
        self.setPath(path)
