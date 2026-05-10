from typing import Self

from PyQt6.QtCore    import Qt, QPointF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsPathItem, QMenu
from PyQt6.QtGui     import QAction

from ....app import settings

from ....core.defs  import PITCH, WIDTH
from ....core.types import Direction, RectHandleId, PortHandleId, DataKind
from ....core.check import checked

from ..properties import PropertyTextSpec

from .port_pin import PortPinMixin
from .node     import PortNodeItem
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
    NODE_CLS = PortNodeItem
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

    @checked
    def __init__(
        self   : Self,
        parent : QGraphicsItem | None = None,
        fresh  : bool = True
    ) -> None:
        QGraphicsPathItem.__init__(self, parent)
        self.initPortPin(fresh)

    @checked
    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
        self.onSettingsChange(scene)

    @checked
    def onSettingsChange(self : Self, scene : "DrawingScene | None" = None) -> None:
        self._setPath(scene)

    @checked
    def initHandles(self : Self) -> None:
        self._handles = {
            PortHandleId.NODE : HandleItem(
                id     = PortHandleId.NODE,
                pos    = QPointF(0, 0),
                kind   = "move",
                parent = self
            ),
            PortHandleId.NAME : HandleItem(
                id     = PortHandleId.NAME,
                pos    = QPointF(0, 0),  # set by _setPath()
                kind   = "move",
                parent = self
            )
        }

    @checked
    def moveHandleBy(self : Self, _ : PortHandleId, d : QPointF) -> None:
        self.setPos(self.pos() + d)

    @checked
    def setDirection(self : Self, value : "Direction") -> None:
        PortPinMixin.setDirection(self, value)
        self._setPath()

    @checked
    def _setPath(self : Self, scene : "DrawingScene | None" = None) -> None:
        # ensure scene resources are available
        if scene is None:
            if (scene := self.scene()) is None:
                return
        item_name = self.settingsName()
        # set path
        self.setPath(scene.resources[item_name][self._direction.value])
        # update name handle position
        settings_path = f"theme/items/{item_name}"
        # standard offset
        name_offset = WIDTH
        # allow for pin
        name_offset += PITCH
        # allow for port size
        port_size = settings().get(f"{settings_path}/size")
        name_offset += port_size
        # allow for pen width
        pen_style = settings().get(f"{settings_path}/line/style")
        if pen_style != Qt.PenStyle.NoPen:
            pen_width = settings().get(f"{settings_path}/line/width")
            name_offset += (pen_width / 2)
        # finalize
        self._handles[PortHandleId.NAME].setPos(QPointF(name_offset, 0))

    @checked
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
