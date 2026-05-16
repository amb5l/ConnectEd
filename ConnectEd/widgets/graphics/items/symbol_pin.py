from typing import Self

from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ....core.defs  import PITCH
from ....core.types import RectHandleId, SymbolPinHandleId, DataKind
from ....core.check import checked

from ..properties import PropertyTextSpec

from .port_pin import PortPinArrowItem, PortPinPathItem

from .mixin.loc       import ItemLocMixin
from .mixin.handle    import ItemHandlesMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView
    from ..views.symbol  import SymbolView


class SymbolPinArrowItem(PortPinArrowItem):
    pass


class SymbolPinItem(
    ItemLocMixin,
    ItemHandlesMixin[SymbolPinHandleId],
    PortPinPathItem
):
    # class attributes
    _NODE_POS   = -PITCH
    _ARROW_CLS  = SymbolPinArrowItem
    _ARROW_POS  = 0
    _PROPERTIES = PortPinPathItem._PROPERTIES | ItemLocMixin._PROPERTIES
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

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        if isinstance(view, SymbolView):
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
        else:
            return []
