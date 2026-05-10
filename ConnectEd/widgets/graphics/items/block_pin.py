from typing import Self

from PyQt6.QtCore    import Qt, QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ....app import settings

from ....core.defs  import WIDTH
from ....core.types import BlockPinHandleId, RectHandleId
from ....core.check import checked

from ..properties import PropertyTextSpec

from .base_pin import BasePinArrowItem, BasePinItem
from .port_pin import PortPinMixin
from .node     import PinNodeItem

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
    NODE_CLS = PinNodeItem
    _ARROW_CLASS = BlockPinArrowItem
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

    @checked
    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
        self.onSettingsChange(scene)

    @checked
    def onSettingsChange(self : Self, scene : "DrawingScene | None" = None) -> None:
        self._setPath(scene)

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action("Edit...", view.ui.editBlockPin),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]

    @checked
    def _setPath(self : Self, scene : "DrawingScene | None" = None) -> None:
        # ensure scene resources are available
        if scene is None:
            if (scene := self.scene()) is None:
                return
        item_name = self.settingsName()
        # set path
        self.setPath(scene.resources[item_name])
        # update name handle position
        arrow_settings_path = f"theme/items/{item_name}Arrow"
        name_offset = settings().get(f"{arrow_settings_path}/size")
        arrow_pen_style = settings().get(f"{arrow_settings_path}/line/style")
        if arrow_pen_style != Qt.PenStyle.NoPen:
            arrow_pen_width = settings().get(f"{arrow_settings_path}/line/width")
            name_offset += (arrow_pen_width / 2)
        name_offset += WIDTH
        self._handles[BlockPinHandleId.NAME].setPos(QPointF(name_offset, 0))