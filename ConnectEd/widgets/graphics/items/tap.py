from typing import Self

from PyQt6.QtCore    import QPointF, QLineF
from PyQt6.QtGui     import QAction
from PyQt6.QtWidgets import QGraphicsLineItem, QMenu

from ....core.defs  import PITCH
from ....core.types import NetState
from ....core.check import checked

from ..properties import PropertiesMixin

from .node   import TapNodeItem

from .mixin import ItemMixin

from .mixin.transform import ItemTransformMixin
from .mixin.paint     import ItemPaintMixin
from .mixin.change    import ItemChangeMixin
from .mixin.xml       import ItemXmlMixin
from .mixin.menu      import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.diagram  import DiagramView
    from ..scenes.diagram import DiagramScene


class TapItem(
    ItemMixin,
    ItemTransformMixin,
    ItemPaintMixin,
    ItemChangeMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin,
    QGraphicsLineItem
):
    # class attributes
    _LINE = QLineF(0, 0, PITCH, PITCH)
    _PROPERTIES = \
        ItemTransformMixin._PROPERTIES_POS | \
        ItemTransformMixin._PROPERTIES_ROTATE | \
        ItemTransformMixin._PROPERTIES_MIRROR

    # instance attributes
    _line  : QLineF
    _node1 : TapNodeItem
    _node2 : TapNodeItem
    _state : NetState

    @checked
    def __init__(
        self  : Self,
        pos   : QPointF,
        fresh : bool = True
    ) -> None:
        QGraphicsLineItem.__init__(self)
        self.setPos(pos)
        self.setLine(self._LINE)
        self.initItem(fresh)
        self._node1 = TapNodeItem(self)
        self._node1.setPos(0, 0)
        self._node2 = TapNodeItem(self)
        self._node2.setPos(PITCH, PITCH)
        self._state = NetState.UNRESOLVED

    @checked
    def onSceneChange(self : Self, scene : "DiagramScene | None") -> None:
        self.onSettingsChange(scene)

    @checked
    def onSettingsChange(self : Self, scene : "DiagramScene | None") -> None:
        if scene is None:
            if (scene := self.scene()) is None:
                return
        self.setPen(scene.resources["Tap"][self._state.value])

    @checked
    def onConnectivityChange(self : Self) -> None:
        # update self._state based on self._node1 and self._node2
        pass

    @checked
    def ctxMenuItems(self : Self, view : "DiagramView") -> list[QAction | QMenu]:
        return [
            view.action("Rotate CW",  lambda: self.rotateCW(),  shortcut="]"),
            view.action("Rotate CCW", lambda: self.rotateCCW(), shortcut="["),
        ]
