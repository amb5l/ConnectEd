from typing import Self

from PyQt6.QtCore    import Qt, QPointF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QMenu, QGraphicsPathItem
from PyQt6.QtGui     import QAction, QPen, QBrush, QPainterPath

from ....app import settings

from ....core.check import checked

from .mixin        import ItemMoveMixin
from .mixin.origin import ItemOriginMixin
from .mixin.change import ItemChangeMixin
from .mixin.shape  import ItemShapeMixin
from .mixin.menu   import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView
    from ..scenes.drawing import DrawingScene
    from .handle          import HandleItem
    from .polyline        import PolylineItem
    from .text            import TextItem
    from .mixin.handle    import ItemHandlesMixin
    from .mixin.grip      import ItemGripMixin


class GripItem(
    ItemMoveMixin,
    ItemChangeMixin,
    ItemShapeMixin,
    ItemMenuMixin,
    QGraphicsPathItem
):
    # class attributes
    _PATH_PREFIX = "Filled" # default path name prefix
    _PATH_NAME : str  # subclass must set this e.g. "Circle"

    # instance attributes
    _path_name_prefix = "Filled"  # default path name prefix
    _path_name_suffix = ""        # default path name suffix
    _path_name : str              # path name
    _path      : QPainterPath     # path
    _brush     : QBrush           # brush

    @checked
    def __init__(
        self   : Self,
        parent : "HandleItem",
        pos    : QPointF | None = None,
        move   : bool = False,
        resize : bool = False
    ) -> None:
        super().__init__(parent)
        self._hshape = QPainterPath()
        self.setPos(pos or QPointF(0, 0))
        self._path_name = self._PATH_NAME
        self.setFlag( self.GraphicsItemFlag.ItemIgnoresTransformations , True  )
        self.setFlag( self.GraphicsItemFlag.ItemIsSelectable           , False )
        self.setFlag( self.GraphicsItemFlag.ItemIsMovable              , False )
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self._brush = QBrush(Qt.BrushStyle.SolidPattern)
        self.setVisible(False)
        self.onSettingsChange()
        settings().changed.connect(self.onSettingsChange)

    @checked
    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
        if scene is not None:
            self.onPathChange(scene)

    @checked
    def onSettingsChange(self : Self) -> None:
        self.prepareGeometryChange()
        self.onSceneChange(self.scene())
        self._brush.setColor(settings().get("theme/grip/color"))
        self.setBrush(self._brush)

    @checked
    def onPathChange(self : Self, scene : "DrawingScene | None" = None) -> None:
        if scene is None:
            scene : "DrawingScene | None" = self.scene()
        if scene is None:
            return
        self.setPath(scene.paths["Grip"][self.fullPathName()])
        self._hshape.clear()
        self._hshape.addRect(self.boundingRect())

    @checked
    def handle(self : Self) -> "HandleItem":
        return self.parentItem()

    @checked
    def item(self : Self) -> "ItemHandlesMixin | ItemGripMixin":
        return self.handle().parentItem()

    @checked
    def pathNamePrefix(self : Self) -> str:
        return self._path_name_prefix

    @checked
    def pathName(self : Self) -> str:
        return self._path_name

    @checked
    def pathNameSuffix(self : Self) -> str:
        return self._path_name_suffix

    @checked
    def fullPathName(self : Self) -> str:
        return self.pathNamePrefix() + self.pathName() + self.pathNameSuffix()

    @checked
    def toXml(self : Self, _ : QXmlStreamWriter) -> None:
        pass

    @checked
    @classmethod
    def fromXml(cls : Self, _ : QXmlStreamReader) -> Self:
        pass


class OriginGripItem(GripItem):
    """Grip for items with an origin."""

    _ORIGIN_PATH_NAME_SUFFIX = "Squared"

    @checked
    def pathNameSuffix(self : Self) -> str:
        item = self.item()
        if hasattr(item, "origin") and item.origin() == self.handle().id():
            return self._ORIGIN_PATH_NAME_SUFFIX
        return ""

    @checked
    def moveBy(self : Self, delta : QPointF) -> None:
        item : "ItemHandlesMixin" = self.item()
        item.moveHandleBy(self.handle().id(), delta)


class MoveGripItem(OriginGripItem):
    """Grip for movable (non resizeable) items."""

    _PATH_NAME = "Circle"

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        entries = [
            view.action("Slide", lambda: view.ui.editSlide([self.item()], self.scenePos())),
            view.action("Move", lambda: view.ui.editMove([self.item()], self.scenePos()))
        ]
        item : "ItemOriginMixin" = self.item()
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


class ResizeGripItem(MoveGripItem):
    """Grip for resizeable items."""

    _PATH_NAME = "Diamond"

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        entries = [
            view.action("Resize", lambda: view.ui.editResize(self, self.scenePos())),
        ]
        entries.extend(MoveGripItem.ctxMenuItems(self, view))
        return entries


class PolylineGripItem(ResizeGripItem):
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


class TextGripItem(ResizeGripItem):
    """Grip for text items."""

    @checked
    def pathNamePrefix(self : Self) -> str:
        item : "TextItem" = self.item()
        name = self.handle().id()
        w = item.width()
        h = item.height()
        c = False  # whether the item dimension(s) for this grip are constrained
        # constrained if top or bottom, and height >= 0.0
        c |= ("Top" in name or "Bottom" in name) and h >= 0.0
        # constrained if left or right, and width >= 0.0
        c |= ("Left" in name or "Right" in name) and w >= 0.0
        return "Filled" if c else "Unfilled"

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
