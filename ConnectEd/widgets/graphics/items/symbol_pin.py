from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ....core.defs  import PITCH
from ....core.types import RectHandleId, SymbolPinHandleId, HandleId, DataKind
from ....core.check import checked

from ..properties import PropertyTextSpec

from .port_pin import PortPinArrowItem, PortPinPathItem
from .handle   import HandleItem
from .grip     import GripItem, MoveGripItem

from .mixin.edge_loc import ItemEdgeLocMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.diagram import DiagramView
    from ..views.symbol  import SymbolView


class SymbolPinArrowItem(PortPinArrowItem):
    pass


class SymbolPinItem(ItemEdgeLocMixin, PortPinPathItem):
    # class attributes
    _NODE_POS   = -PITCH
    _ARROW_CLS  = SymbolPinArrowItem
    _ARROW_POS  = 0
    _PROPERTIES = PortPinPathItem._PROPERTIES | ItemEdgeLocMixin._PROPERTIES
    _PROPERTY_TEXTS = {
            "Name" : PropertyTextSpec(
                cleat=SymbolPinHandleId.NAME, origin=RectHandleId.MIDDLE_LEFT
            )
        }
    _XML_CHILDREN = frozenset({"PropertyText"})

    @classmethod
    def handleIdType(cls) -> type[SymbolPinHandleId]:
        return SymbolPinHandleId

    @classmethod
    def handleIdKind(cls) -> DataKind:
        return DataKind.SYMBOL_PIN_HANDLE

    @classmethod
    def handleGripType(cls, id : HandleId) -> type[GripItem]:
        return MoveGripItem

    @checked
    def initHandles(self : Self) -> None:
        PortPinPathItem.initHandles(self)
        self._handles[SymbolPinHandleId.ORIGIN] = HandleItem(
            id       = SymbolPinHandleId.ORIGIN,
            pos      = QPointF(0, 0),
            grip_cls = MoveGripItem,
            parent   = self
        )

    @checked
    def ctxMenuItems(
        self : Self,
        view : DiagramView,
        spos : QPointF
    ) -> list[QAction | QMenu]:
        if isinstance(view, SymbolView):
            return [
                view.action(
                    "Dot",
                    lambda: view.editPinDot(
                        item=self, enable=not self._dot
                    ),
                    checked=self._dot
                ),
                view.action(
                    "Clock",
                    lambda: view.editPinClk(
                        item=self, enable=not self._clock
                    ),
                    checked=self._clock
                )
            ]
        else:
            return []
