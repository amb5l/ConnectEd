from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtGui     import QPainterPath, QPen

from ....app import logger, settings

from ....core.defs  import Z_DRAWING

from .mixin        import ElementMixin
from .mixin.pos    import ElementPosMixin
from .mixin.line   import ElementLineMixin
from .mixin.fill   import ElementFillMixin
from .mixin.change import ElementChangeMixin
from .mixin.clone  import ElementCloneMixin
from .mixin.xml    import ElementXmlMixin

from .junction import Junction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene
    from .conn_seg import ConnSeg
    from .node     import Node


class ConnVtx(
    ElementMixin,
    ElementPosMixin,
    ElementLineMixin,
    ElementFillMixin,
    ElementChangeMixin,
    ElementCloneMixin,
    ElementXmlMixin,
    QGraphicsPathItem
):
    """Vertex (end point of one or more wire segments).
    Junction appears when there are more than 2 connections to the vertex.
    """
    # class attributes
    Z = Z_DRAWING + 1
    _PATH = "ConnVtx"

    # instance attributes
    _path        : QPainterPath
    _junction    : Junction
    _connections : list["ConnSeg"]

    def __init__(self : Self, parent : "Node | None" = None) -> None:
        QGraphicsPathItem.__init__(self, parent)
        self._connections = []
        self.initElement()
        self._junction = Junction(self)

    def onScenePositionChange(self : Self, _pos : QPointF) -> None:
        """Update all connected segments."""
        for segment in self._connections:
            segment.onGeometryChange()

    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
        if scene is not None:
            self.setPath(scene.paths[self._PATH])

    def onSettingsChange(self : Self) -> None:
        # update visibility
        settings_path = f"theme/elements/{self.__class__.__name__}/visible"
        visible = settings().get(settings_path)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, visible)
        if not visible:
            return
        # update path
        self.onSceneChange(self.scene())

    def updateJunction(self : Self) -> None:
        """Update junction visibility - show if >2 connections."""
        connections = len(self._connections)
        # TODO: special case: parent is node, segments are not colinear
        self._junction.setVisible((connections > 2))
        print(f"updateJunction: {connections}")

    def attach(self : Self, segment : "ConnSeg") -> None:
        if segment not in self._connections:
            self._connections.append(segment)
        self.updateJunction()

    def detach(self : Self, segment : "ConnSeg") -> None:
        if segment not in self._connections:
            logger().warning(f"Segment {segment} not found in connections")
            return
        self._connections.remove(segment)
        self.updateJunction()

    def connections(self : Self) -> list["ConnSeg"]:
        return self._connections
