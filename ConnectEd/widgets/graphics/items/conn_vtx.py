from typing import Self

from PyQt6.QtCore    import QPointF, QXmlStreamWriter
from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtGui     import QPainterPath

from ....app import logger, settings

from ....core.defs  import Z_DRAWING

from .mixin        import ItemMixin
from .mixin.pen    import ItemLineMixin
from .mixin.fill   import ItemFillMixin
from .mixin.change import ItemChangeMixin
from .mixin.clone  import ItemCloneMixin
from .mixin.xml    import ItemXmlMixin

from .junction import Junction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.drawing import DrawingScene
    from .conn_seg import ConnSeg
    from .entry    import Entry


class ConnVtx(
    ItemMixin,
    ItemLineMixin,
    ItemFillMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    QGraphicsPathItem
):
    """Vertex (end point of one or more wire segments).
    Junction appears when there are more than 2 connections to the vertex.
    """
    # class attributes
    Z = Z_DRAWING + 1
    _PATH_NAME = "ConnVtx"

    # instance attributes
    _path        : QPainterPath
    _junction    : Junction
    _connections : list["ConnSeg"]

    def __init__(
        self   : Self,
        pos    : QPointF | None = None,
        parent : "Entry | None" = None
    ) -> None:
        QGraphicsPathItem.__init__(self, parent)
        if pos is not None:
            self.setPos(pos)
        self._connections = []
        self.initItem()
        self._junction = Junction(self)

    def onScenePositionChange(self : Self, _pos : QPointF) -> None:
        """Update all connected segments."""
        for segment in self._connections:
            segment.onGeometryChange()

    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
        if scene is not None:
            self.setPath(scene.paths[self._PATH_NAME])

    def onSettingsChange(self : Self) -> None:
        # update visibility
        settings_path = f"theme/items/{self.__class__.__name__}/visible"
        visible = settings().get(settings_path)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, visible)
        if not visible:
            return
        # update path
        self.onSceneChange(self.scene())

    def updateJunction(self : Self) -> None:
        """Update junction visibility - show if >2 connections."""
        connections = len(self._connections)
        # TODO: special case: parent is entry, segments are not colinear
        self._junction.setVisible((connections > 2))

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

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        """Do not serialise."""
        pass
