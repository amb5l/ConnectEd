from typing      import Self

from PyQt6.QtCore    import Qt, QRectF, QPointF, \
                            QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtGui     import QPen, QBrush, QPainterPath, QAction

from ....app import settings

from . import APType

from .mixin.menu import ElementMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView
    from ..scenes.drawing import DrawingScene
    from .mixin.anchor    import ElementAnchorPointsMixin
    from .anchor_point    import AnchorPoint


class Handle(
    ElementMenuMixin,
    QGraphicsPathItem
):
    # instance attributes
    _parent      : "AnchorPoint"               # parent anchor point
    _element     : "ElementAnchorPointsMixin"  # parent element
    _pen         : QPen                        # pen for drawing
    _brush       : QBrush                      # brush for drawing
    _path_normal : QPainterPath                # path when normal
    _path_origin : QPainterPath                # path when anchor
    _actions     : dict[str, QAction]          # context menu actions

    def __init__(self : Self, parent : "AnchorPoint") -> None:
        super().__init__(parent)
        self._parent = parent
        self._element = parent.parentItem()
        self.setFlag( self.GraphicsItemFlag.ItemIgnoresTransformations , True  )
        self.setFlag( self.GraphicsItemFlag.ItemIsSelectable           , False )
        self.setFlag( self.GraphicsItemFlag.ItemIsMovable              , False )
        self._pen = QPen()
        self._pen.setWidth(0)
        self._pen.setStyle(Qt.PenStyle.SolidLine)
        self._brush = QBrush()
        self._brush.setStyle(Qt.BrushStyle.SolidPattern)
        self._path_normal = QPainterPath()
        self._path_origin = QPainterPath()
        self.onSettingsChange()
        settings().changed.connect(self.onSettingsChange)

    def onSettingsChange(self : Self) -> None:
        self.prepareGeometryChange()
        theme = settings().getTheme("handle")
        self._pen.setColor(theme.line)
        self.setPen(self._pen)
        self._brush.setColor(theme.fill)
        self.setBrush(self._brush)
        self._size = settings().get("display/handle/size")
        r = self._size / 2
        square = QRectF(-r, -r, r*2, r*2)
        # update normal appearance
        self._path_normal.clear()
        if self._parent._type == APType.Resizer: # resizable => circle
            self._path_normal.addEllipse(square)
        else: # not resizable => rhombus
            self._path_normal.moveTo(-r, 0)
            self._path_normal.lineTo(0, -r)
            self._path_normal.lineTo(r, 0)
            self._path_normal.lineTo(0, r)
            self._path_normal.closeSubpath()
        # update origin appearance (square)
        self._path_origin.clear()
        self._path_origin.addRect(square)
        # set current appearance
        is_anchor = hasattr(self._element, "_origin") and \
            self._element._origin == self._parent
        self.onOriginChange(is_anchor)

    def onOriginChange(self : Self, origin : bool) -> None:
        self.setPath(self._path_origin if origin else self._path_normal)

    def getMenuItems(self : Self) -> list[str]:
        items = []
        if self._parent._type == APType.Resizer:
            items.append("Resize")
        if self._parent._type != APType.Static:
            items.append("Move")
        if hasattr(self._element, "setOrigin"):
            items.append("Assign Origin")
        return items

    def moveBy(self : Self, delta : QPointF) -> None:
        self._element.moveAnchorPointBy(self._parent._name, delta)

    def toXml(self : Self, _ : QXmlStreamWriter) -> None:
        pass

    @classmethod
    def fromXml(cls : Self, _ : QXmlStreamReader) -> Self:
        pass

    def ctxMenuMove(
        self : Self,
        _    : bool,
        view : "DrawingView"
    ) -> None:
        view.editMoveBegin([self._element], self.scenePos())
        view.state.go(view.stateEditMove)

    def ctxMenuResize(
        self : Self,
        _    : bool,
        view : "DrawingView"
    ) -> None:
        view.state.go(view.stateEditResize)

    def ctxMenuAssignOrigin(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        from ..scenes.drawing.cmd.edit import cmdEditOrigin
        scene : "DrawingScene" = self.scene()
        scene.undo_stack.push(cmdEditOrigin(
            scene,
            self._element,      # element
            self._parent._name  # name of anchor point
        ))
