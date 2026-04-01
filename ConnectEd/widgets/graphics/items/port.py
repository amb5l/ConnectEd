from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsPathItem, QMenu
from PyQt6.QtGui     import QAction

from ....core.defs  import PITCH
from ....core.types import Direction, RectHandleId, PortHandleId, DataKind

from ..properties import PropertyTextSpec

from .port_pin import PortPinMixin
from .base_pin import _PIN_SIZE
from .handle   import HandleItem

from .mixin.paint  import ItemPaintMixin
from .mixin.pos    import ItemPosMixin
from .mixin.rotate import ItemRotateMixin
from .mixin.handle import ItemHandlesMixin
from .mixin.fill   import ItemFillMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView
    from ..scenes.drawing import DrawingScene


_PORT_SIZE = 6  # documentation - DO NOT CHANGE


class PortItem(
    ItemPaintMixin,
    ItemPosMixin,
    ItemRotateMixin,
    ItemHandlesMixin[PortHandleId],
    ItemFillMixin,
    PortPinMixin,
    QGraphicsPathItem
):
    # class attributes
    _PROPERTIES = \
        PortPinMixin._PROPERTIES_NAME      | \
        PortPinMixin._PROPERTIES_DIR       | \
        PortPinMixin._PROPERTIES_COMMENT   | \
        ItemPosMixin._PROPERTIES_POS       | \
        ItemRotateMixin._PROPERTIES_ROTATE | \
        PortPinMixin._PROPERTIES_LINE      | \
        ItemFillMixin._PROPERTIES_FILL
    _PROPERTY_TEXTS = {
            "Name" : PropertyTextSpec(
                cleat=PortHandleId.NAME, origin=RectHandleId.MIDDLE_LEFT
            )
        }

    @classmethod
    def handleIdType(cls) -> type[PortHandleId]:
        return PortHandleId

    @classmethod
    def handleIdKind(cls) -> DataKind:
        return DataKind.PORT_HANDLE

    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None,
        fresh  : bool = True
    ) -> None:
        QGraphicsPathItem.__init__(self, parent)
        self.initPortPin(fresh)

    def initHandles(self : Self) -> None:
        self._handles = {
            PortHandleId.ENTRY : HandleItem(
                id     = PortHandleId.ENTRY,
                pos    = QPointF(0, 0),
                kind   = "move",
                parent = self
            ),
            PortHandleId.NAME : HandleItem(
                id     = PortHandleId.NAME,
                pos    = QPointF(_PIN_SIZE + _PORT_SIZE + self._PIN_NAME_OFFSET, 0),
                kind   = "move",
                parent = self
            )
        }

    def moveHandleBy(self : Self, _ : PortHandleId, d : QPointF) -> None:
        self.setPos(self.pos() + d)

    def onSceneChange(self : Self, scene : "DrawingScene") -> None:
        self._setPath(scene)

    def setDirection(self : Self, value : "Direction") -> None:
        PortPinMixin.setDirection(self, value)
        self._setPath()

    def _setPath(self : Self, scene : "DrawingScene | None" = None) -> None:
        if scene is None:
            if (scene := self.scene()) is None:
                return
        item_name = self.__class__.__name__.removesuffix("Item")
        self.setPath(scene.resources[item_name][self._direction.value])

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
