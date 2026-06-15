from typing import Self
from enum   import StrEnum

from PyQt6.QtCore    import Qt, QPointF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QMenu, QGraphicsPathItem
from PyQt6.QtGui     import QAction, QPen

from ....app import settings

from ....core.check import checked

from ..scenes import withScene

from .role import ChromeItem

from .mixin           import ItemMoveMixin
from .mixin.transform import ItemTransformMixin
from .mixin.change    import ItemChangeMixin
from .mixin.menu      import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView
    from ..scenes.drawing import DrawingScene
    from .handle          import HandleItem
    from .mixin.handle    import ItemHandlesMixin
    from .mixin.grip      import ItemGripMixin


class GripShape(StrEnum):
    SQUARE  = "Square"   # origin
    CIRCLE  = "Circle"   # resize/move
    DIAMOND = "Diamond"  # vertex
    ARROW   = "Arrow"    # segment
    STAR    = "Star"     # hotspot


class GripItem(
    ChromeItem,
    ItemMoveMixin,
    ItemChangeMixin,
    ItemMenuMixin,
    QGraphicsPathItem
):
    @checked
    def __init__(
        self   : Self,
        parent : "HandleItem",
        pos    : QPointF | None = None,
        move   : bool = False,
        resize : bool = False
    ) -> None:
        super().__init__(parent)
        self.setPos(pos or QPointF(0, 0))
        self.setFlag( self.GraphicsItemFlag.ItemIgnoresTransformations , True  )
        self.setFlag( self.GraphicsItemFlag.ItemIsSelectable           , False )
        self.setFlag( self.GraphicsItemFlag.ItemIsMovable              , False )
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setVisible(False)
        self.onSettingsChanged()
        settings().changed.connect(self.onSettingsChanged)

    @checked
    def onSettingsChanged(self : Self) -> None:
        if (scene := self.scene()) is not None:
            self.onSceneChanged(scene)

    @checked
    def onSceneChanged(self : Self, scene : "DrawingScene | None") -> None:
        if scene is None:
            return
        self.setPen(scene.resources.pen("Grip"))
        self.setBrush(scene.resources.brush("Grip"))
        self.updatePath(scene)

    @withScene
    @checked
    def updatePath(self : Self, scene : "DrawingScene | None" = None) -> None:
        raise NotImplementedError("Subclasses must implement this method")

    @checked
    def handle(self : Self) -> "HandleItem":
        return self.parentItem()

    @checked
    def item(self : Self) -> "ItemHandlesMixin | ItemGripMixin":
        return self.handle().parentItem()

    @checked
    def moveBy(
        self   : Self,
        dx_d   : float | QPointF,
        dy     : float | None = None
    ) -> None:
        delta = dx_d if isinstance(dx_d, QPointF) \
            else QPointF(dx_d, dy if dy is not None else 0.0)
        item : "ItemHandlesMixin" = self.item()
        item.moveHandleBy(self.handle().id(), delta)

    @checked
    def toXml(self : Self, _ : QXmlStreamWriter) -> None:
        pass

    @checked
    @classmethod
    def fromXml(cls : Self, _ : QXmlStreamReader) -> Self:
        pass


class GripShapeMixin:
    _SHAPE : GripShape

    @withScene
    @checked
    def updatePath(self : Self, scene : "DrawingScene | None" = None) -> None:
        self.setPath(scene.resources.path("Grip", self._SHAPE))


class OriginGripShapeMixin:
    # class attributes
    _NORMAL_SHAPE : GripShape
    _ORIGIN_SHAPE : GripShape

    @withScene
    @checked
    def updatePath(
        self  : Self | GripItem,
        scene : "DrawingScene | None" = None
    ) -> None:
        item          = self.item()
        normal_shape  = getattr(item, "_NORMAL_GRIP_SHAPE", self._NORMAL_SHAPE)
        origin_shape  = getattr(item, "_ORIGIN_GRIP_SHAPE", self._ORIGIN_SHAPE)
        shape = origin_shape if self.handle().isOrigin() else normal_shape
        self.setPath(scene.resources.path("Grip", shape))


class MoveGripItem(OriginGripShapeMixin, GripItem):
    """Grip for moving the item."""

    # class attributes
    _NORMAL_SHAPE = GripShape.CIRCLE
    _ORIGIN_SHAPE = GripShape.SQUARE

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView", _spos : QPointF) -> list[QAction | QMenu]:
        entries = [
            view.action("Slide", lambda: view.ui.editSlide([self.item()], self.scenePos())),
            view.action("Move", lambda: view.ui.editMove([self.item()], self.scenePos()))
        ]
        item : "ItemTransformMixin" = self.item()
        if item.origin() is not None:
            h : HandleItem = self.parentItem()
            entries.extend([
                view.separator(),
                view.action(
                    "Assign Origin",
                    lambda: view.ui.editAssignOrigin(self.item(), h.id())
                )
            ])
        return entries


class ResizeGripItem(OriginGripShapeMixin, GripItem):
    """Grip for resizing the item."""

    # class attributes
    _NORMAL_SHAPE = GripShape.CIRCLE
    _ORIGIN_SHAPE = GripShape.SQUARE

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView", _spos : QPointF) -> list[QAction | QMenu]:
        entries = [
            view.action("Resize", lambda: view.ui.editResize(self, self.scenePos())),
        ]
        entries.extend(MoveGripItem.ctxMenuItems(self, view, _spos))
        return entries


class VertexGripItem(GripShapeMixin, GripItem):
    """Grip for item vertices."""

    # class attributes
    _SHAPE = GripShape.DIAMOND


class SegmentGripItem(GripShapeMixin, GripItem):
    """Grip for item segments."""

    # class attributes
    _SHAPE = GripShape.ARROW
