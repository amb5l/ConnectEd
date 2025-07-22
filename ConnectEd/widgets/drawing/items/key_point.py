__all__ = ["KP", "KPReverse", "KeyPoint", "KPDef", "KPManager"]

from typing      import Self, Optional
from enum        import Enum
from dataclasses import dataclass

from PyQt6.QtCore    import Qt, QRectF, QPointF, QObject, pyqtSignal, \
                            QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, \
                            QWidget, QGraphicsView
from PyQt6.QtGui     import QPainter, QPen, QBrush, QPainterPath, QAction

from ....core import logger

from . import ElementMenuMixin

from .... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ... import DrawingView


@dataclass(frozen=True)
class KPLoc:
    name : str
    h    : float
    v    : float

class KP(Enum):
    TOP_LEFT      = KPLoc( "Top Left"      , 0.0 , 0.0 )
    TOP_CENTER    = KPLoc( "Top Center"    , 0.5 , 0.0 )
    TOP_RIGHT     = KPLoc( "Top Right"     , 1.0 , 0.0 )
    CENTER_LEFT   = KPLoc( "Center Left"   , 0.0 , 0.5 )
    CENTER        = KPLoc( "Center"        , 0.5 , 0.5 )
    CENTER_RIGHT  = KPLoc( "Center Right"  , 1.0 , 0.5 )
    BOTTOM_LEFT   = KPLoc( "Bottom Left"   , 0.0 , 1.0 )
    BOTTOM_CENTER = KPLoc( "Bottom Center" , 0.5 , 1.0 )
    BOTTOM_RIGHT  = KPLoc( "Bottom Right"  , 1.0 , 1.0 )

KPReverse = {
    "Top Left"      : KP.TOP_LEFT,
    "Top Center"    : KP.TOP_CENTER,
    "Top Right"     : KP.TOP_RIGHT,
    "Center Left"   : KP.CENTER_LEFT,
    "Center"        : KP.CENTER,
    "Center Right"  : KP.CENTER_RIGHT,
    "Bottom Left"   : KP.BOTTOM_LEFT,
    "Bottom Center" : KP.BOTTOM_CENTER,
    "Bottom Right"  : KP.BOTTOM_RIGHT
}

class KeyPoint(ElementMenuMixin, QGraphicsItem):
    # class variables
    Z_DELTA = 1

    # instance variables
    _manager : "KPManager"
    _loc     : KP                 # location of key point in parent
    _resize  : bool               # whether the key point is a resize grip
    _cleat   : bool               # whether the key point can be a cleat
    _rect    : QRectF             # bounding rect
    _shape   : QPainterPath       # shape for hit detection
    _pen     : QPen               # pen for drawing
    _brush   : QBrush             # brush for drawing
    _normal  : QPainterPath       # drawn shape when normal
    _anchor  : QPainterPath       # drawn shape when anchor
    _path    : QPainterPath       # drawn shape
    _actions : dict[str, QAction]

    def __init__(
        self    : Self,
        manager : "KPManager",
        loc     : KP,
        resize  : bool = False,
        cleat   : bool = False
    ) -> None:
        super().__init__(manager.element)
        self.setZValue(self.parentItem().zValue() + self.Z_DELTA)
        self.setFlag( self.GraphicsItemFlag.ItemIsMovable              , True )
        self.setFlag( self.GraphicsItemFlag.ItemIgnoresTransformations , True )
        self._manager = manager
        self._loc     = loc
        self._resize  = resize
        self._cleat   = cleat
        self._pen     = QPen()
        self._brush   = QBrush()
        self._path    = QPainterPath()
        self._rect    = QRectF()
        self._shape   = QPainterPath()
        self._pen.setWidth(0)
        self._pen.setStyle(Qt.PenStyle.SolidLine)
        self._brush.setStyle(Qt.BrushStyle.SolidPattern)
        self._normal = QPainterPath()
        self._anchor = QPainterPath()
        self.onSettingsChange()
        hub.settings.changed.connect(self.onSettingsChange)
        self._actions = []
        self._manager.anchorChanged.connect(self.onGeometryChange)

    def getMenuItems(self : Self) -> list[str]:
        items = []
        if self._resize:
            items.append("Resize")
        items.append("Move")
        if self._manager.element._ANCHORED:
            items.append("Assign Anchor")
        return items

    def boundingRect(
        self : Self,
        view : Optional[QGraphicsView] = None
    ) -> QRectF:
        return self._rect

    def shape(self : Self) -> QPainterPath:
        return self._shape

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawPath(self._path)

    def moveBy(self : Self, dx : float, dy : float) -> None:
        self.parentItem().moveKeyPoint(self._loc, QPointF(dx, dy))

    def onSettingsChange(self : Self) -> None:
        theme = hub.settings.getTheme("key_point")
        self._pen.setColor(theme.line)
        self._brush.setColor(theme.line)
        self._radius = hub.settings.get("display/key_point/radius")
        self.onGeometryChange()

    def onGeometryChange(self : Self) -> None:
        self.prepareGeometryChange()
        r = self._radius
        # update for hit testing
        self._rect.setCoords(-r, -r, r, r)
        self._shape.clear()
        self._shape.addRect(self._rect)
        # update normal appearance
        self._normal.clear()
        if self._resize: # resizable => circle
            self._normal.addEllipse(self._rect)
        else: # not resizable => rhombus
            self._normal.moveTo(-r, 0)
            self._normal.lineTo(0, -r)
            self._normal.lineTo(r, 0)
            self._normal.lineTo(0, r)
            self._normal.closeSubpath()
        # update anchor appearance
        self._anchor.clear()
        self._anchor.addRect(self._rect)
        # set appearance
        self._path = self._anchor if self._manager.anchor == self else self._normal

    def isMoveable(self : Self) -> bool:
        return self._resize

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
        from ..views.drawing.defs import DrawingViewState as State
        view.editMoveBegin([self.parentItem()], self.scenePos())
        view.state.go(view.stateEditMove2)

    def ctxMenuResize(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        from ..views.drawing.defs import DrawingViewState as State
        view.editMoveBegin([self], self.scenePos())
        view.state.go(view.stateEditMove2)

    def ctxMenuAssignAnchor(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        self._manager.setAnchor(self._loc)

@dataclass
class KPDef:
    """KeyPoint Definition"""
    loc    : KP   # location
    resize : bool # whether the key point can be used for resize
    cleat  : bool # whether the key point can be a cleat

class KPManager(QObject):
    element       : QGraphicsItem         # parent element
    key_points    : dict[KP, KeyPoint]
    anchor        : Optional[KeyPoint]
    anchor_loc    : Optional[KP]
    anchor_offset : QPointF

    anchorChanged = pyqtSignal(KP)

    def __init__(
        self    : Self,
        parent  : QGraphicsItem,
        kp_defs : list[KPDef],
        anchor  : Optional[KP] = None
    ) -> None:
        super().__init__()
        self.element = parent
        self.anchor = None
        self.key_points = {
            x.loc: KeyPoint(self, x.loc, x.resize, x.cleat) for x in kp_defs
        }
        self.anchor_loc = None
        self.anchor_offset = QPointF(0, 0)
        if parent._ANCHORED:
            if anchor:
                self.setAnchor(anchor)
            else:
                self.setAnchor(kp_defs[0].loc)
        else:
            if anchor:
                logger.error("anchor specified for non-anchorable element")
        self.onSelectionChange(parent.isSelected())

    def onSelectionChange(self : Self, selected : bool) -> None:
        for kp in self.key_points.values():
            kp.setVisible(selected)

    def setAnchor(self, anchor : KP) -> None:
        self.anchor = self.key_points[anchor]
        self.anchor_loc = anchor
        self.anchor_offset = self.getKeyPointPos(anchor)
        self.anchorChanged.emit(anchor)
        for kp in self.key_points.values():
            kp.onGeometryChange()

    def getKeyPointPos(self, kp : KP) -> QPointF:
        rect = self.element.boundingRect()
        return QPointF(kp.value.h * rect.width(), kp.value.v * rect.height())

    def updatePositions(self : Self) -> None:
        rect = self.element._rect
        for kp_loc in self.key_points.keys():
            new_pos = QPointF(
                kp_loc.value.h * rect.width(),
                kp_loc.value.v * rect.height()
            )
            if kp_loc != self.key_points[kp_loc]:
                self.key_points[kp_loc].setPos(new_pos)
        if self.anchor_loc is not None:
            self.anchor_offset = self.getKeyPointPos(self.anchor_loc)
