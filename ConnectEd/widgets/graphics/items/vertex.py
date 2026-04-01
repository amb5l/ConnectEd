from typing import Self
from enum   import StrEnum

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsPathItem

from ....app import logger

from ....core.defs  import Z_DRAWING

from .mixin        import ItemMixin
from .mixin.shape  import ItemShapeMixin
from .mixin.change import ItemChangeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene
    from .segment  import SegmentItem
    from .port_pin import PortPinMixin


class VertexItem(
    ItemMixin,
    ItemShapeMixin,
    ItemChangeMixin,
    QGraphicsPathItem
):
    class State(StrEnum):
        UNCONNECTED = "unconnected"
        CONNECTED   = "connected"
        JUNCTION    = "junction"

    Z = Z_DRAWING + 1
    _JUNCTION_THRESHOLD = 3

    # instance attributes
    _id          : int | None
    _state       : State
    _connections : list["SegmentItem"]

    def __init__(
        self   : Self,
        pos    : QPointF | None = None,
        id     : int | None = None,
        parent : "PortPinMixin | None" = None
    ) -> None:
        super().__init__(parent)
        if pos is not None:
            self.setPos(pos)
        self._id = id
        self._state = self.State.UNCONNECTED
        self._connections = []
        self.initItem()

    def id(self : Self) -> int | None:
        return self._id

    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
        if scene is not None:
            self.onSettingsChange(scene)

    def onSettingsChange(self : Self, scene : "DrawingScene | None" = None) -> None:
        if scene is None:
            if (scene := self.scene()) is None:
                return
        item_name = self.settingsName()  # "Entry" or "Vertex"
        state_str = self._state.value  # e.g. "unconnected"
        self.setPen(scene.resources[item_name][state_str]["pen"])
        self.setBrush(scene.resources[item_name][state_str]["brush"])
        self.setPath(scene.resources[item_name][state_str]["path"])

    def onScenePositionChange(self : Self, _pos : QPointF) -> None:
        """Update all connected segments."""
        for segment in self._connections:
            segment.onGeometryChange()

    def onConnectionChange(self : Self, scene : "DrawingScene | None" = None) -> None:
        if scene is None:
            if (scene := self.scene()) is None:
                return
        n = len(self._connections)
        self.state = \
            self.State.JUNCTION    if n >= self._JUNCTION_THRESHOLD else \
            self.State.CONNECTED   if n >= 1 else \
            self.State.UNCONNECTED
        item_name = self.settingsName()
        state_str = self._state.value
        self.setPath(scene.resources[item_name][state_str]["path"])

    def attach(self : Self, segment : "SegmentItem") -> None:
        if segment not in self._connections:
            self._connections.append(segment)
        self.onConnectionChange()

    def detach(self : Self, segment : "SegmentItem") -> None:
        if segment not in self._connections:
            logger().warning(f"Segment {segment} not found in connections")
            return
        self._connections.remove(segment)
        self.onConnectionChange()

    def connections(self : Self) -> list["SegmentItem"]:
        return self._connections


class EntryItem(VertexItem):
    _JUNCTION_THRESHOLD = 2
