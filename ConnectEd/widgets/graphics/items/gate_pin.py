from typing import Self

from PyQt6.QtCore    import QPointF, QXmlStreamWriter
from PyQt6.QtWidgets import QGraphicsItem, QMenu
from PyQt6.QtGui     import QAction

from ....core.check import checked
from ....core.defs  import PITCH
from ....core.types import GatePinHandleId, DataKind

from .role import FunctionalItem

from .port_pin import PortPinArrowItem, PortPinPathItem
from .handle   import HandleItem
from .grip     import MoveGripItem

from .mixin.transform import ItemTransformMixin
from .mixin.handle    import ItemHandlesMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.diagram import DiagramView


class GatePinArrowItem(PortPinArrowItem):
    pass


class GatePinItem(
    FunctionalItem,
    ItemTransformMixin,
    ItemHandlesMixin[GatePinHandleId],
    PortPinPathItem
):
    # class attributes
    _NODE_POS  = -PITCH
    _ARROW_CLS = GatePinArrowItem
    _ARROW_POS = 0

    @classmethod
    def handleIdType(cls) -> type[GatePinHandleId]:
        return GatePinHandleId

    @classmethod
    def handleIdKind(cls) -> DataKind:
        return DataKind.GATE_PIN_HANDLE

    def settingsName(self : Self) -> str:
        return "GatePin"

    @checked
    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None,
        fresh  : bool = True  # unused
    ) -> None:
        self._length = PITCH
        super().__init__(parent)
        self._extension = 0

    @checked
    def initHandles(self : Self) -> None:
        PortPinPathItem.initHandles(self)
        self._handles[GatePinHandleId.ORIGIN] = HandleItem(
            id       = GatePinHandleId.ORIGIN,
            pos      = QPointF(0, 0),
            grip_cls = MoveGripItem,
            parent   = self
        )

    @checked
    def moveHandleBy(self : Self, _ : GatePinHandleId, d : QPointF) -> None:
        self.setPos(self.pos() + d)

    def inverted(self : Self) -> bool:
        return self._dot

    @checked
    def setInverted(self : Self, value : bool) -> None:
        self._dot = value
        self._updateGraphics()

    @checked
    def ctxMenuItems(self : Self, view : "DiagramView", _spos : QPointF) -> list[QAction | QMenu]:
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

    def resourcesName(self : Self) -> str:
        return "BufGatePin"


class OrGatePinItem(GatePinItem):
    _NODE_POS  = -(PITCH + 4)
    _ARROW_POS = -4

    def resourcesName(self : Self) -> str:
        return "OrGatePin"
