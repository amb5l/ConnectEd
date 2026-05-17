from typing import Self
from enum   import StrEnum

from PyQt6.QtCore    import Qt, QPointF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QMenu, QGraphicsPathItem
from PyQt6.QtGui     import QAction, QPen, QPainterPath

from ....app import settings

from ....core.check import checked

from ..scenes import withScene

from .mixin           import ItemMoveMixin
from .mixin.transform import ItemTransformMixin
from .mixin.change    import ItemChangeMixin
from .mixin.menu      import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView
    from ..scenes.drawing import DrawingScene
    from .handle          import HandleItem
    from .polyline        import PolylineItem
    from .text            import TextItem
    from .mixin.handle    import ItemHandlesMixin
    from .mixin.grip      import ItemGripMixin


class GripShape(StrEnum):
    SQUARE  = "Square"   # origin
    CIRCLE  = "Circle"   # resize/move
    DIAMOND = "Diamond"  # vertex
    ARROW   = "Arrow"    # segment


class GripItem(
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
        self.onSettingsChange()
        settings().changed.connect(self.onSettingsChange)

    @checked
    def onSettingsChange(self : Self) -> None:
        self.onSceneChange()

    @withScene
    @checked
    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
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
    def moveBy(self : Self, delta : QPointF) -> None:
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
    _ORIGIN_SHAPE = GripShape.SQUARE

    @withScene
    @checked
    def updatePath(
        self  : Self | GripItem,
        scene : "DrawingScene | None" = None
    ) -> None:
        is_origin = self.handle().isOrigin()
        self.setPath(scene.resources.path(
            "Grip",
            self._ORIGIN_SHAPE if is_origin else self._NORMAL_SHAPE
        ))


class MoveGripItem(OriginGripShapeMixin, GripItem):
    """Grip for moving the item."""

    # class attributes
    _NORMAL_SHAPE = GripShape.CIRCLE

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
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

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        entries = [
            view.action("Resize", lambda: view.ui.editResize(self, self.scenePos())),
        ]
        entries.extend(MoveGripItem.ctxMenuItems(self, view))
        return entries

class TextResizeGripItem(ResizeGripItem):
    """Grip for resizing text items."""

    @checked
    def moveSave(self : Self) -> tuple[QPointF, float | None, float | None]:
        item : "TextItem" = self.item()
        return self.scenePos(), item.width(), item.height()

    @checked
    def moveRestore(
        self  : Self,
        state : tuple[QPointF, float | None, float | None]
    ) -> None:
        pos, width, height = state
        item : "TextItem" = self.item()
        self.moveBy(pos - self.scenePos())
        item.setWidth(width)
        item.setHeight(height)


class PolylineResizeGripItem(ResizeGripItem):
    """Grip for resizing Polyline items."""

    @checked
    def moveSave(self : Self) -> tuple[QPointF, list[QPointF]]:
        item : "PolylineItem" = self.item()
        return self.scenePos(), [v.pos() for v in item.vertices()]

    @checked
    def moveRestore(
        self  : Self,
        state : tuple[QPointF, list[QPointF]]
    ) -> None:
        item : "PolylineItem" = self.item()
        pos, vertices = state
        self.moveBy(pos - self.scenePos())
        for i, v in enumerate(item.vertices()):
            v.setPos(vertices[i])


class VertexGripItem(GripShapeMixin, GripItem):
    """Grip for item vertices."""

    # class attributes
    _SHAPE = GripShape.DIAMOND


class SegmentGripItem(GripShapeMixin, GripItem):
    """Grip for item segments."""

    # class attributes
    _SHAPE = GripShape.ARROW
