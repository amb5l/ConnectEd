from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from .....app import logger

from .....core.check import checked
from .....core.types import DataKind, EdgeLoc, Edge

from ...properties import InherentProperty

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..block import BlockItem


class ItemLocMixin:
    """
    Block and symbol pins use this mixin for edge location positioning.
    """

    # class attributes
    _PROPERTIES = {
        "Edge" : InherentProperty(
            kind   = DataKind.EDGE,
            getter = lambda self: self.loc().edge,
            setter = lambda self, value: self.setLocEdge(value)
        ),
        "Offset" : InherentProperty(
            kind   = DataKind.FLOAT,
            getter = lambda self: self.loc().offset,
            setter = lambda self, value: self.setLocOffset(value)
        )
    }

    # instance attributes
    _loc : EdgeLoc

    @checked
    def initLoc(self : Self) -> None:
        self._loc = EdgeLoc()

    @checked
    def onParentChanged(self : Self, parent : QGraphicsItem | None) -> None:
        """Update position when parent changes."""
        if hasattr(self, '_loc') \
        and parent is not None \
        and self._loc.edge is not None:
            self.setLoc(self._loc)
            # Edge/rotation may already be set on the orphan; re-propagate
            # autoflip now that the pin has a parent and scene chain.
            self.onRotationChanged(self.rotation())
            self.onMirrorChanged()
        if parent is not None and (scene := self.scene()) is not None \
        and hasattr(self, "onSceneChanged"):
            self.onSceneChanged(scene)

    def onRotationChanged(self : Self | QGraphicsItem, _angle : float) -> None:
        """Propagate rotation change to children."""
        for child in self.childItems():
            if hasattr(child, "onSceneRotationChanged"):
                child.onSceneRotationChanged()

    def onMirrorChanged(self : Self | QGraphicsItem) -> None:
        """Propagate mirror change to children."""
        for child in self.childItems():
            if hasattr(child, "onSceneMirrorChanged"):
                child.onSceneMirrorChanged()

    def loc(self : Self) -> EdgeLoc:
        return self._loc

    @checked
    def setLoc(self : Self, loc : EdgeLoc) -> None:
        self._loc = loc
        self.prepareGeometryChange()
        match loc.edge:
            case Edge.LEFT   : angle = 0
            case Edge.RIGHT  : angle = 180
            case Edge.TOP    : angle = 90
            case Edge.BOTTOM : angle = 270
            case _ :
                logger().error(f"Invalid edge: {loc.edge}")
                angle = 0
        self.setRotation(angle)
        parent : BlockItem = self.parentItem()
        if loc.edge is None or loc.offset is None:
            return
        QGraphicsItem.setPos(self, parent.loc2pos(loc) if parent else QPointF())

    @checked
    def setLocEdge(self : Self, edge : Edge) -> None:
        self.setLoc(EdgeLoc(Edge(edge), self._loc.offset))
        self.properties.signalChanges("Edge")

    @checked
    def setLocOffset(self : Self, offset : float) -> None:
        self.setLoc(EdgeLoc(self._loc.edge, offset))
        self.properties.signalChanges("Offset")

    @checked
    def locSnap(self : Self, loc : EdgeLoc, snap : QPointF | None = None) -> EdgeLoc:
        e = loc.edge
        if snap is None:
            d = loc.offset
        elif loc.edge in [Edge.LEFT, Edge.RIGHT]:
            d = round(loc.offset / snap.x()) * snap.x()
        else:
            d = round(loc.offset / snap.y()) * snap.y()
        return EdgeLoc(e, d)

    def pos(self : Self) -> QPointF:
        raise NotImplementedError("pos is not implemented for ItemLocMixin")

    def setPos(self : Self, _ : QPointF) -> None:
        raise NotImplementedError("setPos is not implemented for ItemLocMixin")
