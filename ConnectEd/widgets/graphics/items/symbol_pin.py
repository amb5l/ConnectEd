from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ....core.types import RectHandleId, SymbolPinHandleId, DataKind

from ..properties import PropertyTextSpec

from .port_pin import PortPinMixin
from .base_pin import BasePinArrowItem, BasePinItem, \
                      BasePinDotMixin, BasePinClockMixin, \
                      _PIN_CLK_SIZE

from .mixin.pos     import ItemPosMixin
from .mixin.rotate  import ItemRotateMixin
from .mixin.handle  import ItemHandlesMixin
from .mixin.line    import ItemLineMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView
    from ..scenes.drawing import DrawingScene


class SymbolPinArrowItem(BasePinArrowItem):
    pass


class SymbolPinItem(
    ItemPosMixin,
    ItemRotateMixin,
    ItemHandlesMixin[SymbolPinHandleId],
    BasePinDotMixin,
    BasePinClockMixin,
    BasePinItem
):
    # class attributes
    _ARROW_CLASS = SymbolPinArrowItem
    _PROPERTIES = \
        PortPinMixin._PROPERTIES_NAME | \
        PortPinMixin._PROPERTIES_DIR | \
        PortPinMixin._PROPERTIES_COMMENT | \
        BasePinDotMixin._PROPERTIES_DOT | \
        BasePinClockMixin._PROPERTIES_CLOCK | \
        ItemPosMixin._PROPERTIES_POS | \
        ItemRotateMixin._PROPERTIES_ROTATE | \
        ItemLineMixin._PROPERTIES_LINE
    _PROPERTY_TEXTS = {
            "Name" : PropertyTextSpec(
                cleat=SymbolPinHandleId.NAME, origin=RectHandleId.MIDDLE_LEFT
            )
        }

    @classmethod
    def handleIdType(cls) -> type[SymbolPinHandleId]:
        return SymbolPinHandleId

    @classmethod
    def handleIdKind(cls) -> DataKind:
        return DataKind.SYMBOL_PIN_HANDLE

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
        self.setPath(scene.resources["SymbolPin"][key])
        self._handles[SymbolPinHandleId.NAME].setPos(QPointF(
            self._PIN_NAME_OFFSET + (_PIN_CLK_SIZE if self._clock else 0), 0
        ))
