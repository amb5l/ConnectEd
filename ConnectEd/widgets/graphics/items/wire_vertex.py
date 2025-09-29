from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtGui     import QPainterPath, QPen

from ....app import logger, settings

from .mixin        import ElementMixin
from .mixin.pos    import ElementPosMixin
from .mixin.fill   import ElementFillMixin
from .mixin.change import ElementChangeMixin
from .mixin.clone  import ElementCloneMixin
from .mixin.xml    import ElementXmlMixin

from .junction import Junction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene
    from .wire_segment    import WireSegment
    from .node            import Node


class WireVertex(
    ElementMixin,
    ElementPosMixin,
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
    _PATH = "WireVertex"

    # instance attributes
    _path        : QPainterPath
    _pen         : QPen
    _junction    : Junction
    _connections : list["WireSegment"]

    def __init__(self : Self, parent : "Node | None" = None) -> None:
        QGraphicsPathItem.__init__(self, parent)
        self._connections = []
        self._junction = Junction(self)
        self.initFill()
        self.onSettingsChange()
        settings().changed.connect(self.onSettingsChange)

    def onScenePositionChange(self : Self, _pos : QPointF) -> None:
        """Update all connected segments."""
        for segment in self._connections:
            segment.onGeometryChange()

    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
        if scene is not None:
            self.setPath(scene.paths[self._PATH])

    def onSettingsChange(self : Self) -> None:
        # update visibility
        visible = settings().get("theme/elements/WireVertex/visible")
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, visible)
        if not visible:
            return
        # update path
        self.onSceneChange(self.scene())

    def updateJunction(self : Self) -> None:
        """Update junction visibility - show if >2 connections."""
        vertex : "WireVertex" = self.parentItem()
        connections = len(self._connections)
        # special case: parent is node, segments are not colinear
        node : "Node | None" = vertex.parentItem()


        self._junction.setVisible((connections > 2))

    def connect(self : Self, segment : "WireSegment") -> None:
        if segment not in self._connections:
            self._connections.append(segment)
        self.updateJunction()

    def disconnect(self : Self, segment : "WireSegment") -> None:
        if segment not in self._connections:
            logger().warning(f"Segment {segment} not found in connections")
            return
        self._connections.remove(segment)
        self.updateJunction()
