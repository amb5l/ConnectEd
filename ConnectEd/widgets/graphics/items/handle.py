from typing import Self
from types  import NoneType
from enum   import Flag

from PyQt6.QtCore    import Qt, QPointF, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtGui     import QPen, QBrush, QPainterPath

from ....app import settings

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

    def onSceneChange(self : Self, scene : "DrawingScene | NoneType") -> None:
        if scene is not None:
            self.setPath(scene.paths[self._PATH])
        print(f"{self.__class__.__name__}.onSceneChange : {self._PATH}")

    def onSettingsChange(self : Self) -> None:
        self.prepareGeometryChange()
        self.onSceneChange(self.scene())
        self._brush.setColor(settings().get(f"theme/selected/fill"))
        self.setBrush(self._brush)

    def moveBy(self : Self, delta : QPointF) -> None:
        parent : "AnchorPoint" = self.parentItem()
        self._element.moveAnchorPointBy(parent.name, delta)

    def toXml(self : Self, _ : QXmlStreamWriter) -> None:
        pass

    @classmethod
    def fromXml(cls : Self, _ : QXmlStreamReader) -> Self:
        pass

    def getMenuItems(self : Self) -> list[str]:
        return self._MENU.copy()

    def ctxMenuMove(
        self : Self,
        _    : bool,
        view : "DrawingView"
    ) -> None:
        from ..scenes.drawing.interaction import EditMoveInteraction
        view.interaction = EditMoveInteraction(
            self.scene(), self._element, self.scenePos()
        )
        view.state.go(view.stateEditMove)

    def ctxMenuResize(
        self : Self,
        _    : bool,
        view : "DrawingView"
    ) -> None:
        from ..scenes.drawing.interaction import EditMoveInteraction
        view.interaction = EditMoveInteraction(
            self.scene(), self, self.scenePos()
        )
        view.state.go(view.stateEditResize)

    def ctxMenuAssignOrigin(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        from ..scenes.drawing.cmd.edit import cmdEditOrigin
        scene : "DrawingScene" = self.scene()
        parent : "AnchorPoint" = self.parentItem()
        scene.undo_stack.push(cmdEditOrigin(
            scene,
            self._element,      # element
            parent.name         # name of anchor point
        ))


class Grip(Handle):
    _PATH = "Grip"

    def getMenuItems(self : Self) -> list[str]:
        r = self._MENU.copy()
        if hasattr(self._element, "_origin"):
            r.extend(["-", "Assign Origin"])
        return r


class MoveGrip(Grip):
    _MENU = ["Move"]


class ResizeGrip(Grip):
    _MENU = ["Resize", "Move"]


class Origin(Handle):
    _PATH = "Origin"

    def __init__(
        self   : Self,
        parent : "AnchorPoint",
        move   : bool = False,
        resize : bool = False
    ) -> None:
        print(f"Origin.__init__ : {parent}")
        super().__init__(parent, move, resize)

    def getMenuItems(self : Self) -> list[str]:
        return []
