from typing import Self

from PyQt6.QtCore    import Qt, QPointF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QMenu, QGraphicsPathItem
from PyQt6.QtGui     import QAction, QPen, QBrush, QPainterPath

from ....app import settings

from .mixin.origin import ItemOriginMixin
from .mixin.change import ItemChangeMixin
from .mixin.menu   import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView
    from ..scenes.drawing import DrawingScene
    from .handle          import Handle
    from .unitext         import UniText
    from .mixin.handle    import ItemHandlesMixin
    from .mixin.grip      import ItemGripMixin


class Grip(
    ItemChangeMixin,
    ItemMenuMixin,
    QGraphicsPathItem
):
    # class attributes
    _PATH_PREFIX = "Filled" # default path name prefix
    _PATH_NAME : str  # subclass must set this e.g. "Circle"

    # instance attributes
    _path_name_prefix = "Filled"  # default path name prefix
    _path_name_suffix = ""        # default path name suffix
    _path_name   : str            # path name
    _path        : QPainterPath   # path
    _brush       : QBrush         # brush

    def __init__(
        self   : Self,
        parent : "Handle",
        pos    : QPointF | None = None,
        move   : bool = False,
        resize : bool = False
    ) -> None:
        super().__init__(parent)
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

    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
        if scene is not None:
            self.onPathChange(scene)

    def onSettingsChange(self : Self) -> None:
        self.prepareGeometryChange()
        self.onSceneChange(self.scene())
        self._brush.setColor(settings().get("theme/grip/color"))
        self.setBrush(self._brush)

    def onPathChange(self : Self, scene : "DrawingScene | None" = None) -> None:
        if scene is None:
            scene : "DrawingScene | None" = self.scene()
        if scene is None:
            return
        self.setPath(scene.paths["Grip"][self.fullPathName()])

    def handle(self : Self) -> "Handle":
        return self.parentItem()

    def item(self : Self) -> "ItemHandlesMixin | ItemGripMixin":
        return self.handle().parentItem()

    def pathNamePrefix(self : Self) -> str:
        return self._path_name_prefix

    def pathName(self : Self) -> str:
        return self._path_name

    def pathNameSuffix(self : Self) -> str:
        return self._path_name_suffix

    def fullPathName(self : Self) -> str:
        return self.pathNamePrefix() + self.pathName() + self.pathNameSuffix()

    def toXml(self : Self, _ : QXmlStreamWriter) -> None:
        pass

    @classmethod
    def fromXml(cls : Self, _ : QXmlStreamReader) -> Self:
        pass


class OriginGrip(Grip):
    """Grip for items with an origin."""

    _ORIGIN_PATH_NAME_SUFFIX = "Squared"

    def pathNameSuffix(self : Self) -> str:
        item = self.item()
        if hasattr(item, "getOrigin") and item.getOrigin() == self.handle().name():
            return self._ORIGIN_PATH_NAME_SUFFIX
        return ""

    def moveBy(self : Self, delta : QPointF) -> None:
        self.item().moveHandleBy(self.handle().name(), delta)


class MoveGrip(OriginGrip):
    """Grip for movable (non resizeable) items."""

    _PATH_NAME = "Circle"

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        entries = [
            view.action("Slide", lambda: view.ui.editSlide([self._item], self.scenePos())),
            view.action("Move", lambda: view.ui.editMove([self._item], self.scenePos()))
        ]
        item : "ItemOriginMixin" = self.item()
        if item.getOrigin() is not None:
            h : Handle = self.parentItem()
            entries.extend([
                view.separator(),
                view.action(
                    "Assign Origin",
                    lambda: view.ui.editAssignOrigin(self.item(), h.name())
                )
            ])
        return entries


class ResizeGrip(MoveGrip):
    """Grip for resizeable items."""

    _PATH_NAME = "Diamond"

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        entries = [
            view.action("Resize", lambda: view.ui.editResize(self, self.scenePos())),
        ]
        entries.extend(MoveGrip.ctxMenuItems(self, view))
        return entries


class TextGrip(ResizeGrip):
    """Grip for text items."""

    def pathNamePrefix(self : Self) -> str:
        item : "UniText" = self.item()
        name = self.handle().name()
        w = item.width()
        h = item.height()
        c = False  # whether the item dimension(s) for this grip are constrained
        # constrained if top or bottom, and height is not None
        c |= ("Top" in name or "Bottom" in name) and h is None
        # constrained if left or right, and width is not None
        c |= ("Left" in name or "Right" in name) and w is None
        return "Filled" if c else "Unfilled"
