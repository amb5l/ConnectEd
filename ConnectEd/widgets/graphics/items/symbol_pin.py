from typing import Self

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem, QMenu
from PyQt6.QtGui     import QAction

from ....core.defs import PITCH

from .mixin.pos_rot import ItemPosRotMixin
from .mixin.line    import ItemLineMixin

from .port_pin import PortPinMixin
from .base_pin import BasePinArrow, BasePin, \
                      BasePinDotMixin, BasePinClockMixin, \
                      _PIN_CLK_SIZE

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView
    from ..scenes.drawing import DrawingScene


class SymbolPinArrow(BasePinArrow):
    pass


class SymbolPin(ItemPosRotMixin, BasePinDotMixin, BasePinClockMixin, BasePin):
    # class attributes
    _ARROW_CLASS = SymbolPinArrow
    _PROPERTY_SPECS = \
        PortPinMixin._PROPERTY_SPECS_NAME | \
        PortPinMixin._PROPERTY_SPECS_DIR | \
        PortPinMixin._PROPERTY_SPECS_COMMENT | \
        BasePinDotMixin._PROPERTY_SPECS_DOT | \
        BasePinClockMixin._PROPERTY_SPECS_CLOCK | \
        ItemPosRotMixin._PROPERTY_SPECS_POS_ROT | \
        ItemLineMixin._PROPERTY_SPECS_LINE

    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None,
        bare   : bool = False
    ) -> None:
        super().__init__(parent, bare)

    def moveHandleBy(self : Self, _ : str, delta : QPointF) -> None:
        """Move the entire SymbolPin when any grip is dragged."""
        self.setPos(self.pos() + delta)

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action(
                "Dot",
                lambda: view.ui.editSymbolPinDot(self, not self._dot),
                checked=self._dot
            ),
            view.action(
                "Clock",
                lambda: view.ui.editSymbolPinClock(self, not self._clock),
                checked=self._clock
            )
        ]

    def _setPath(self : Self, scene : "DrawingScene | None" = None) -> None:
        if scene is None:
            if (scene := self.scene()) is None:
                return
        key = (self._dot, self._clock)
        self.setPath(scene.paths["SymbolPin"][key])
        self._handles["Name"].setPos(QPointF(
            self._AP_NAME_OFFSET + (_PIN_CLK_SIZE if self._clock else 0), 0
        ))
