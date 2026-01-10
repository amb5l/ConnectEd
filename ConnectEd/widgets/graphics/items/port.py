from typing import Self

from PyQt6.QtWidgets import QGraphicsItem, QGraphicsPathItem, QMenu
from PyQt6.QtGui     import QAction

from ....app import settings

from .mixin.paint   import ItemPaintMixin
from .mixin.pos_rot import ItemPosRotMixin
from .mixin.fill    import ItemFillMixin

from .port_pin import PortPinMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView
    from ..scenes.drawing import DrawingScene
    from . import SignalDirection


class Port(
    ItemPosRotMixin,
    ItemPaintMixin,
    ItemFillMixin,
    PortPinMixin,
    QGraphicsPathItem
):
    # class attributes
    _AP_NAME_OFFSET = 1.5
    _PROPERTY_SPECS = \
        PortPinMixin._PROPERTY_SPECS_NAME | \
        PortPinMixin._PROPERTY_SPECS_DIR | \
        PortPinMixin._PROPERTY_SPECS_COMMENT | \
        ItemPosRotMixin._PROPERTY_SPECS_POS_ROT | \
        ItemFillMixin._PROPERTY_SPECS_FILL

    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None,
        bare   : bool = False
    ) -> None:
        QGraphicsPathItem.__init__(self, parent)
        self.initPortPin(bare)
        self.onSettingsChange()

    def onSettingsChange(self : Self) -> None:
        size = settings().get("theme/items/Port/size")
        self.getHandle("Name").setPos(size + self._AP_NAME_OFFSET, 0)

    def onSceneChange(self : Self, scene : "DrawingScene") -> None:
        self._setPath(scene)

    def setDirection(self : Self, value : "SignalDirection") -> None:
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
