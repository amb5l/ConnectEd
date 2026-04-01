from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ....core.types import BlockPinHandleId, RectHandleId

from ..properties import PropertyTextSpec

from .base_pin import BasePinArrowItem, BasePinItem, _INT_ARROW_SIZE
from .port_pin import PortPinMixin
from .handle   import HandleItem

from .mixin.loc    import ItemLocMixin
from .mixin.handle import ItemBlockPinHandlesMixin


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView
    from ..scenes.drawing import DrawingScene


class BlockPinArrowItem(BasePinArrowItem):
    pass


class BlockPinItem(ItemLocMixin, ItemBlockPinHandlesMixin, BasePinItem):
    # class attributes
    _ARROW_CLASS = BlockPinArrowItem
    _PIN_NAME_OFFSET  = _INT_ARROW_SIZE + 1.5
    _PROPERTIES = \
        PortPinMixin._PROPERTIES_NAME | \
        PortPinMixin._PROPERTIES_DIR | \
        ItemLocMixin._PROPERTIES_LOC | \
        PortPinMixin._PROPERTIES_COMMENT
    _PROPERTY_TEXTS = {
            "Name" : PropertyTextSpec(
                cleat=BlockPinHandleId.NAME, origin=RectHandleId.MIDDLE_LEFT
            )
        }

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action("Edit...", view.ui.editBlockPin),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]

    def _setPath(self : Self, scene : "DrawingScene | None" = None) -> None:
        if scene is None:
            if (scene := self.scene()) is None:
                return
        self.setPath(scene.resources["BlockPin"])
