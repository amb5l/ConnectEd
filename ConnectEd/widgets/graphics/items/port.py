from typing import Self

from PyQt6.QtWidgets import QGraphicsItem, QGraphicsPathItem, QMenu
from PyQt6.QtGui     import QAction

from ....app import settings

from .mixin.paint import ItemPaintMixin
from .mixin.pos   import ItemPosMixin
from .mixin.fill  import ItemFillMixin

from .port_pin import PortPinText, PortPinMixin
from .entry    import Entry

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView
    from ..scenes.drawing import DrawingScene
    from . import SignalDirection


class PortEntry(Entry):
    pass


class PortName(PortPinText):
    pass


class PortComment(PortPinText):
    pass


class Port(
    ItemPosMixin,
    ItemPaintMixin,
    ItemFillMixin,
    PortPinMixin,
    QGraphicsPathItem
):
    # class attributes
    _AP_NAME_OFFSET = 1.5
    _PROPERTY_SPECS = \
        ItemPosMixin._PROPERTY_SPECS_POS | \
        PortPinMixin._PROPERTY_SPECS | \
        ItemFillMixin._PROPERTY_SPECS_FILL

    @classmethod
    def _getEntryClass(cls) -> type[PortEntry]:
        return PortEntry

    @classmethod
    def _getNameClass(cls) -> type[PortName]:
        return PortName

    @classmethod
    def _getCommentClass(cls) -> type[PortComment]:
        return PortComment

    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None,
        bare   : bool = False
    ) -> None:
        QGraphicsPathItem.__init__(self, parent)
        self.initPortPin(bare)

    def onSettingsChange(self : Self) -> None:
        size = settings().get("theme/items/Port/size")
        self.getAnchorPoint("Name").setPos(size + self._AP_NAME_OFFSET, 0)

    def onSceneChange(self : Self, scene : "DrawingScene") -> None:
        self._setPath(scene)

    def setRotation(self : Self, angle : float) -> None:
        super().setRotation(angle)
        for property_text in self._property_texts.values():
            property_text.compensateRotation()

    @property
    def direction(self : Self) -> "SignalDirection":
        return super().direction

    @direction.setter
    def direction(self : Self, value : "SignalDirection") -> None:
        super(Port, Port).direction.__set__(self, value)
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
            view.action("Edit...", view.ui.editPort),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editProperties(self))
        ]
