from typing import Self

from PyQt6.QtGui     import QAction
from PyQt6.QtWidgets import QMenu

from .mixin.loc import ItemLocMixin

from .port_pin import PortPinText, PortPinMixin
from .base_pin import BasePinArrow, BasePinEntry, BasePin, _INT_ARROW_SIZE

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView
    from ..scenes.drawing import DrawingScene


class BlockPinArrow(BasePinArrow):
    pass


class BlockPinEntry(BasePinEntry):
    pass


class BlockPinName(PortPinText):
    pass


class BlockPinComment(PortPinText):
    pass


class BlockPin(ItemLocMixin, BasePin):
    # class attributes
    _AP_NAME_OFFSET  = _INT_ARROW_SIZE + 1.5
    _PROPERTY_SPECS = \
        ItemLocMixin._PROPERTY_SPECS_LOC | \
        PortPinMixin._PROPERTY_SPECS

    @classmethod
    def _getArrowClass(cls) -> type[BlockPinArrow]:
        return BlockPinArrow

    @classmethod
    def _getEntryClass(cls) -> type[BlockPinEntry]:
        return BlockPinEntry

    @classmethod
    def _getNameClass(cls) -> type[BlockPinName]:
        return BlockPinName

    @classmethod
    def _getCommentClass(cls) -> type[BlockPinComment]:
        return BlockPinComment

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action("Edit...", view.ui.editBlockPin),
            view.separator()
        ] + super().ctxMenuItems()

    def _setPath(self : Self, scene : "DrawingScene | None" = None) -> None:
        if scene is None:
            if (scene := self.scene()) is None:
                return
        self.setPath(scene.paths["BlockPin"])
