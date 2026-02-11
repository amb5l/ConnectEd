from typing import Self

from PyQt6.QtWidgets import QGraphicsItem, QGraphicsPathItem, QMenu
from PyQt6.QtGui     import QAction

from ....app         import settings

from ....core.types import Direction, BlockPinHandleId

from .mixin.paint  import ItemPaintMixin
from .mixin.pos    import ItemPosMixin
from .mixin.rotate import ItemRotateMixin
from .mixin.fill   import ItemFillMixin

from .port_pin import PortPinMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView
    from ..scenes.drawing import DrawingScene


class PortItem(
    ItemPosMixin,
    ItemRotateMixin,
    ItemPaintMixin,
    ItemFillMixin,
    PortPinMixin,
    QGraphicsPathItem
):
    # class attributes
    _AP_NAME_OFFSET = 1.5
    _PROPERTIES = \
        PortPinMixin._PROPERTIES_NAME | \
        PortPinMixin._PROPERTIES_DIR | \
        PortPinMixin._PROPERTIES_COMMENT | \
        ItemPosMixin._PROPERTIES_POS | \
        ItemRotateMixin._PROPERTIES_ROTATE | \
        ItemFillMixin._PROPERTIES_FILL

    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None,
        fresh  : bool = True
    ) -> None:
        QGraphicsPathItem.__init__(self, parent)
        self.initPortPin(fresh)
        self.onSettingsChange()

    def onSettingsChange(self : Self) -> None:
        size = settings().get("theme/items/Port/size")
        self.getHandle(BlockPinHandleId.NAME).setPos(size + self._AP_NAME_OFFSET, 0)

    def onSceneChange(self : Self, scene : "DrawingScene") -> None:
        self._setPath(scene)

    def setDirection(self : Self, value : "Direction") -> None:
        PortPinMixin.setDirection(self, value)
        self._setPath()

    def _setPath(self : Self, scene : "DrawingScene | None" = None) -> None:
        if scene is None:
            if (scene := self.scene()) is None:
                return
        if  self.__class__.__name__ in scene.paths \
        and self._direction.value in scene.paths[self.__class__.__name__]:
            path = scene.paths[self.__class__.__name__][self._direction.value]
            self.setPath(path)

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action(
                "Rotate CW", lambda: view.ui.editRotateCW([self]), shortcut="]"
            ),
            view.action(
                "Rotate CCW", lambda: view.ui.editRotateCCW([self]), shortcut="["
            ),
            view.action("Edit...", view.ui.editPort),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]
