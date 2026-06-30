from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ....core.defs  import PITCH
from ....core.types import HandleId, RectHandleId, BlockPinHandleId, DataKind
from ....core.check import checked

from ..properties import PropertyTextSpec

from .grip import GripItem, ResizeGripItem
from .port_pin import PortPinArrowItem, PortPinLineItem

from .mixin.edge_loc import ItemEdgeLocMixin


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.diagram import DiagramView


class BlockPinArrowItem(PortPinArrowItem):
    pass


class BlockPinItem(ItemEdgeLocMixin, PortPinLineItem):
    # class attributes
    _NODE_POS   = -PITCH
    _ARROW_CLS  = BlockPinArrowItem
    _ARROW_POS  = 0
    _PROPERTIES = PortPinLineItem._PROPERTIES | ItemEdgeLocMixin._PROPERTIES
    _PROPERTY_TEXTS = \
        {
            "Name" : PropertyTextSpec(
                cleat=BlockPinHandleId.NAME, origin=RectHandleId.MIDDLE_LEFT
            )
        }
    _XML_CHILDREN = frozenset({"PropertyText"})

    @classmethod
    def handleIdType(cls) -> type[BlockPinHandleId]:
        return BlockPinHandleId

    @classmethod
    def handleIdKind(cls) -> DataKind:
        return DataKind.BLOCK_PIN_HANDLE

    @classmethod
    def handleGripType(cls, id : HandleId) -> type[GripItem]:
        return ResizeGripItem

    def resourcesName(self : Self) -> str:
        return "BlockPin"

    @checked
    def ctxMenuItems(
        self : Self,
        view : DiagramView,
        spos : QPointF
    ) -> list[QAction | QMenu]:
        return [
            view.action("Edit...", view.editBlockPin),
            view.separator(),
            view.action("Appearance...", lambda: view.editAppearance(self)),
            view.action("Properties...", lambda: view.editItemProperties(self))
        ]
