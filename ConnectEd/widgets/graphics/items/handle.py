from typing import Self

from PyQt6.QtCore    import Qt, QPointF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsPathItem, QMenu
from PyQt6.QtGui     import QPen, QBrush, QPainterPath, QAction

from ....app import settings, window

from .mixin.change import ElementChangeMixin
from .mixin.menu   import ElementMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView
    from ..scenes.drawing import DrawingScene
    from .mixin.anchor    import ElementAnchorPointsMixin
    from .anchor_point    import AnchorPoint


class Handle(
    ElementChangeMixin,
    ElementMenuMixin,
    QGraphicsPathItem
):
    # class attributes
    _PATH = "Handle"
    _MENU : list[str]

    # instance attributes
    _element : "ElementAnchorPointsMixin"  # parent element
    _path    : QPainterPath                # path
    _brush   : QBrush                      # brush

    def __init__(
        self   : Self,
        parent : "AnchorPoint",
        move   : bool = False,
        resize : bool = False
    ) -> None:
        super().__init__(parent)
        self._element = parent.parentItem()
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
            self.setPath(scene.paths[self._PATH])

    def onSettingsChange(self : Self) -> None:
        self.prepareGeometryChange()
        self.onSceneChange(self.scene())
        self._brush.setColor(settings().get(f"theme/selected/fill"))
        self.setBrush(self._brush)

    def moveBy(self : Self, delta : QPointF) -> None:
        parent : "AnchorPoint" = self.parentItem()
        self._element.moveAnchorPointBy(parent.name(), delta)

    def toXml(self : Self, _ : QXmlStreamWriter) -> None:
        pass

    @classmethod
    def fromXml(cls : Self, _ : QXmlStreamReader) -> Self:
        pass

    def ctxMenuItems(self : Self) -> list[QAction | QMenu]:
        l = []
        if hasattr(self._element, "_origin"):
            l.extend(window().actions.ctxAssignOrigin)
        return l


class Grip(Handle):
    _PATH = "Grip"

class MoveGrip(Grip):
    def ctxMenuItems(self : Self) -> list[QAction | QMenu]:
        return [
            window().actions.editMove,
            self.ctxMenuSeparator()
        ] + super().ctxMenuItems()


class ResizeGrip(Grip):
    def ctxMenuItems(self : Self) -> list[QAction | QMenu]:
        return [
            window().actions.editResize,
            window().actions.editMove,
            self.ctxMenuSeparator()
        ] + super().ctxMenuItems()


class Origin(Handle):
    _PATH = "Origin"

    def __init__(
        self   : Self,
        parent : "AnchorPoint",
        move   : bool = False,
        resize : bool = False
    ) -> None:
        super().__init__(parent, move, resize)

    def ctxMenuItems(self : Self) -> list[QAction | QMenu]:
        return []
