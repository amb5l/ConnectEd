from typing      import Self

from PyQt6.QtCore    import Qt, QRectF, QPointF, \
                            QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsPathItem, QStyleOptionGraphicsItem, QWidget
from PyQt6.QtGui     import QPainter, QPen, QBrush, QPainterPath, QAction

from . import ElementMenuMixin

from .key_point import KeyPoint

from .... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ... import DrawingView
    from . import ElementKeypointsMixin


class Grip(
    ElementMenuMixin,
    QGraphicsPathItem
):
    # class variables
    Z_DELTA = 1

    # instance variables
    _key_point   : KeyPoint                 # parent key point
    _element     : "ElementKeypointsMixin"  # parent element
    _pen         : QPen                     # pen for drawing
    _brush       : QBrush                   # brush for drawing
    _path_normal : QPainterPath             # path when normal
    _path_anchor : QPainterPath             # path when anchor
    _actions     : dict[str, QAction]       # context menu actions

    def __init__(self : Self, parent : KeyPoint) -> None:
        super().__init__(parent)
        self._key_point = parent
        self._element = parent.parentItem()
        self.setZValue(self.parentItem().zValue() + self.Z_DELTA)
        self.setFlag( self.GraphicsItemFlag.ItemIgnoresTransformations , True  )
        self.setFlag( self.GraphicsItemFlag.ItemIsSelectable           , False )
        self.setFlag( self.GraphicsItemFlag.ItemIsMovable              , False )
        self._pen = QPen()
        self._pen.setWidth(0)
        self._pen.setStyle(Qt.PenStyle.SolidLine)
        self._brush = QBrush()
        self._brush.setStyle(Qt.BrushStyle.SolidPattern)
        self._path_normal = QPainterPath()
        self._path_anchor = QPainterPath()
        self.onSettingsChange()
        hub.settings.changed.connect(self.onSettingsChange)
        self._actions = []

    def onSettingsChange(self : Self) -> None:
        self.prepareGeometryChange()
        theme = hub.settings.getTheme("grip")
        self._pen.setColor(theme.line)
        self.setPen(self._pen)
        self._brush.setColor(theme.fill)
        self.setBrush(self._brush)
        self._size = hub.settings.get("display/grip/size")
        r = self._size / 2
        square = QRectF(-r, -r, r*2, r*2)
        # update normal appearance
        self._path_normal.clear()
        if self._key_point._resize: # resizable => circle
            self._path_normal.addEllipse(square)
        else: # not resizable => rhombus
            self._path_normal.moveTo(-r, 0)
            self._path_normal.lineTo(0, -r)
            self._path_normal.lineTo(r, 0)
            self._path_normal.lineTo(0, r)
            self._path_normal.closeSubpath()
        # update anchor appearance (square)
        self._path_anchor.clear()
        self._path_anchor.addRect(square)
        # set current appearance
        is_anchor = hasattr(self._element, "anchor") and \
            self._element.getAnchorLoc() == self._key_point.getLoc()
        self.onAnchorChange(is_anchor)

    def onAnchorChange(self : Self, anchor : bool) -> None:
        self.setPath(self._path_anchor if anchor else self._path_normal)

    def getMenuItems(self : Self) -> list[str]:
        items = []
        if self._key_point._resize:
            items.append("Resize")
        items.append("Move")
        if hasattr(self._element, "setAnchorLoc"):
            items.append("Assign Anchor")
        return items

    def moveBy(self : Self, dx : float, dy : float) -> None:
        self._element.moveKeyPoint(self._key_point.getLoc(), QPointF(dx, dy))

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        pass

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        pass

    def ctxMenuMove(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        view.editMoveBegin([self._element], self.scenePos())
        view.state.go(view.stateEditMove2)

    def ctxMenuResize(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        view.editMoveBegin([self], self.scenePos())
        view.state.go(view.stateEditMove2)

    def ctxMenuAssignAnchor(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        self._element.setAnchorLoc(self._key_point.getLoc())
