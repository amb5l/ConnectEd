from typing import Self

from PyQt6.QtGui     import QAction
from PyQt6.QtWidgets import QMenu

from .mixin.loc import ItemLocMixin

from .port_pin import PortPinMixin
from .base_pin import BasePinArrow, BasePin, _INT_ARROW_SIZE

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView
    from ..scenes.drawing import DrawingScene


class BlockPinArrow(BasePinArrow):
    pass


class BlockPin(ItemLocMixin, BasePin):
    # class attributes
    _ARROW_CLASS = BlockPinArrow
    _AP_NAME_OFFSET  = _INT_ARROW_SIZE + 1.5
    _PROPERTY_SPECS = \
        PortPinMixin._PROPERTY_SPECS_NAME | \
        PortPinMixin._PROPERTY_SPECS_DIR | \
        ItemLocMixin._PROPERTY_SPECS_LOC | \
        PortPinMixin._PROPERTY_SPECS_COMMENT

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
        self.setPath(scene.paths["BlockPin"])
