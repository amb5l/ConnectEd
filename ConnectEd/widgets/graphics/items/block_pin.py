from typing import Self

from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ....core.defs  import PITCH
from ....core.types import BlockPinHandleId, RectHandleId
from ....core.check import checked

from ..properties import PropertyTextSpec

from .port_pin import PortPinArrowItem, PortPinItem

from .mixin.loc    import ItemLocMixin
from .mixin.handle import ItemBlockPinHandlesMixin


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView


class BlockPinArrowItem(PortPinArrowItem):
    pass


class BlockPinItem(ItemLocMixin, ItemBlockPinHandlesMixin, PortPinItem):
    # class attributes
    _NODE_POS  = -PITCH
    _ARROW_CLS = BlockPinArrowItem
    _ARROW_POS = 0
    _PROPERTIES = \
        PortPinItem._PROPERTIES               | \
        ItemLocMixin._PROPERTIES_LOC
    _PROPERTY_TEXTS = \
        {
            "Name" : PropertyTextSpec(
                cleat=BlockPinHandleId.NAME, origin=RectHandleId.MIDDLE_LEFT
            )
        }

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action("Edit...", view.ui.editBlockPin),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]
