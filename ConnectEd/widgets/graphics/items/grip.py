from typing import Self

from PyQt6.QtCore    import Qt, QPointF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QMenu, QGraphicsItem, QGraphicsPathItem
from PyQt6.QtGui     import QAction, QPen, QBrush, QPainterPath

from ....app import settings

from .mixin.origin import ItemOriginMixin
from .mixin.change import ItemChangeMixin
from .mixin.menu   import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView
    from ..scenes.drawing import DrawingScene
    from .anchor_point import AnchorPoint
    from .mixin.grip import ItemGripMixin


class Grip(
    ItemChangeMixin,
    ItemMenuMixin,
    QGraphicsPathItem
):
    # class attributes
    _PATH_NAME = None  # subclass must set this e.g. "Circle"

    # instance attributes
    _item      : "ItemGripMixin"  # parent item
    _path_name : str              # path name
    _path      : QPainterPath     # path
    _brush     : QBrush           # brush

    def __init__(
        self   : Self,
        parent : QGraphicsItem,
        pos    : QPointF | None = None,
        move   : bool = False,
        resize : bool = False
    ) -> None:
        super().__init__(parent)
        if pos is None:
            pos = QPointF()
        self.setPos(pos)
        self._item = parent.parentItem()
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
            self.setPath(scene.paths["Grip"][self._path_name])

    def onSettingsChange(self : Self) -> None:
        self.prepareGeometryChange()
        self.onSceneChange(self.scene())
        self._brush.setColor(settings().get("theme/grip/color"))
        self.setBrush(self._brush)

    def item(self : Self) -> "ItemGripMixin":
        ap : AnchorPoint = self.parentItem()
        return ap.parentItem()

    def toXml(self : Self, _ : QXmlStreamWriter) -> None:
        pass

    @classmethod
    def fromXml(cls : Self, _ : QXmlStreamReader) -> Self:
        pass


class APGrip(Grip):
    """Grip for anchor points. Base class for move and resize grips."""

    _PATH_NAME = "Circle"
    _ORIGIN_PATH_NAME = "Square"

    def __init__(
        self   : Self,
        parent : "AnchorPoint",
        pos    : QPointF | None = None,
        move   : bool = False,
        resize : bool = False
    ) -> None:
        super().__init__(parent, pos, move, resize)

    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
        """Override to update path based on origin status."""
        if scene is not None:
            self.onOriginChange()

    def onOriginChange(self : Self | QGraphicsItem) -> None:
        ap : "AnchorPoint" = self.parentItem()
        item = ap.parentItem()
        if not isinstance(item, ItemOriginMixin):
            # Item doesn't have an origin point, just use regular path
            self._path_name = self._PATH_NAME
            scene : "DrawingScene" = self.scene()
            if scene:
                self.setPath(scene.paths["Grip"][self._path_name])
            return
        if item.getOrigin() == ap.name():
            self._path_name = self._ORIGIN_PATH_NAME
        else:
            self._path_name = self._PATH_NAME
        scene : "DrawingScene" = self.scene()
        if scene:
            self.setPath(scene.paths["Grip"][self._path_name])

    def moveBy(self : Self, delta : QPointF) -> None:
        parent : "AnchorPoint" = self.parentItem()
        self._item.moveAnchorPointBy(parent.name(), delta)


class MoveGrip(APGrip):
    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        entries = [
            view.action("Slide", view.ui.editSlide),
            view.action("Move", view.ui.editMove)
        ]
        if isinstance(self._item, ItemOriginMixin):
            ap : AnchorPoint = self.parentItem()
            entries.extend([
                view.separator(),
                view.action(
                    "Assign Origin",
                    lambda: view.ui.editAssignOrigin(self.item(), ap.name())
                )
            ])
        return entries


class ResizeGrip(MoveGrip):
    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        entries = [
            view.action("Resize", lambda: view.ui.editResize(self)),
        ]
        entries.extend(MoveGrip.ctxMenuItems(self, view))
        return entries
