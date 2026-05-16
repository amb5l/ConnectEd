from typing import Self

from PyQt6.QtCore    import QXmlStreamWriter
from PyQt6.QtWidgets import QGraphicsItem, QMenu
from PyQt6.QtGui     import QAction

from ....core.defs  import PITCH

from .mixin.transform import ItemTransformMixin
from .mixin.handle    import ItemGatePinHandlesMixin

from .port_pin import PortPinArrowItem, PortPinPathItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.diagram import DiagramView


class GatePinArrowItem(PortPinArrowItem):
    pass


class GatePinItem(ItemTransformMixin, ItemGatePinHandlesMixin, PortPinPathItem):
    # class attributes
    _NODE_POS  = -PITCH
    _ARROW_CLS = GatePinArrowItem
    _ARROW_POS = 0

    def settingsName(self : Self) -> str:
        return "GatePin"

    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None,
        fresh  : bool = True  # unused
    ) -> None:
        self._length = PITCH
        super().__init__(parent)
        self._extension = 0

    def inverted(self : Self) -> bool:
        return self._dot

    def setInverted(self : Self, value : bool) -> None:
        self._dot = value
        self._updateGraphics()

    def ctxMenuItems(self : Self, view : "DiagramView") -> list[QAction | QMenu]:
        return [
            view.action(
                "Active Low",
                lambda: view.ui.editSymbolPinDot(self, not self._dot),
                checked=self._dot
            )
        ]

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        pass  # exclude from XML


class BufGatePinItem(GatePinItem):
    _NODE_POS  = -(PITCH + 2)
    _ARROW_POS = -2

    def settingsName(self : Self) -> str:
        return "GatePin"


class OrGatePinItem(GatePinItem):
    _NODE_POS  = -(PITCH + 4)
    _ARROW_POS = -4

    def settingsName(self : Self) -> str:
        return "GatePin"
