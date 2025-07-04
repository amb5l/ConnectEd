__all__ = ["KP", "KPReverse", "KeyPoint", "KPDef", "KPManager"]

from typing      import Self, Optional
from enum        import Enum
from dataclasses import dataclass

from PyQt6.QtCore    import Qt, QRectF, QPointF, QObject, pyqtSignal, \
                            QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, \
                            QWidget, QGraphicsView, QMenu
from PyQt6.QtGui     import QPainter, QPen, QBrush, QPainterPath

from . import CustomGraphicsItemMixin

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

class KeyPoint(QGraphicsItem):
    # class variables
    Z_DELTA = 1
    _MENU = None
    _MENU_ITEM_NAMES = [
        "Assign Anchor"
    ]
    getMenu = CustomGraphicsItemMixin.getMenu

    # instance variables
    _manager : "KPManager"
    _loc     : KP # parent's key point location
    _grip    : bool
    _cleat   : bool
    _pen     : QPen
    _brush   : QBrush
    _rect    : QRectF
    _rhombus : QPainterPath
    _shape   : QPainterPath
    _menu    : QMenu

    def __init__(
        self    : Self,
        manager : "KPManager",
        loc     : KP,
        grip    : bool = False,
        cleat   : bool = False
    ) -> None:
        super().__init__(manager.element)
        self.setZValue(self.parentItem().zValue() + self.Z_DELTA)
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsMovable              , True )
        self.setFlag( f.ItemIgnoresTransformations , True )
        self._manager = manager
        self._loc     = loc
        self._grip    = grip
        self._cleat   = cleat
        self._pen     = QPen()
        self._brush   = QBrush()
        self._rect    = QRectF()
        self._rhombus = QPainterPath()
        self._shape   = QPainterPath()
        self._pen.setWidth(0)
        self._pen.setStyle(Qt.PenStyle.SolidLine)
        self._brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.onSettingsChange()
        hub.settings.change.connect(self.onSettingsChange)
        self._menu = CustomGraphicsItemMixin.getMenu(self.__class__)

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
        if self._manager.anchor is None or self._manager.anchor == self:
            painter.drawRect(self._rect)
        else:
            painter.drawPath(self._rhombus)

    def moveBy(self : Self, dx : float, dy : float) -> None:
        self.parentItem().moveKeyPoint(self._loc, QPointF(dx, dy))

    def onSettingsChange(self : Self) -> None:
        theme = hub.settings.getTheme("key_point")
        self._pen.setColor(theme.line)
        self._brush.setColor(theme.fill)
        r = hub.settings.get("display/key_point/radius")
        self._rect.setCoords(-r, -r, r, r)
        self._rhombus.clear()
        self._rhombus.moveTo(  0 , -r )
        self._rhombus.lineTo(  r ,  0 )
        self._rhombus.lineTo(  0 ,  r )
        self._rhombus.lineTo( -r ,  0 )
        self._rhombus.closeSubpath()
        self._shape.clear()
        self._shape.addRect(self._rect)

    def isMoveable(self : Self) -> bool:
        return self._grip

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        pass

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        pass

    def ctxMenuAssignAnchor(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        self._manager.setAnchor(self._loc)

@dataclass
class KPDef:
    loc   : KP
    grip  : bool
    cleat : bool

class KPManager(QObject):
    element       : QGraphicsItem         # parent element
    key_points    : dict[KP, KeyPoint]
    anchor        : Optional[KeyPoint]
    anchor_loc    : Optional[KP]
    anchor_offset : QPointF

    change = pyqtSignal()

    def __init__(
        self    : Self,
        parent  : QGraphicsItem,
        kp_defs : list[KPDef],
        anchor  : Optional[KP] = None
    ) -> None:
        super().__init__()
        self.element = parent
        self.key_points = {
            x.loc: KeyPoint(self, x.loc, x.grip, x.cleat) for x in kp_defs
        }
        self.anchor = None
        self.anchor_loc = None
        self.anchor_offset = QPointF(0, 0)
        if anchor:
            self.setAnchor(anchor)
        else:
            for kp_def in kp_defs:
                if not kp_def.grip:
                    self.setAnchor(kp_def.loc)
                    break

    def setAnchor(self, anchor : KP) -> None:
        self.anchor = self.key_points[anchor]
        self.anchor_loc = anchor
        self.anchor_offset = self.getKeyPointPos(anchor)
        self.element.update()

    def getKeyPointPos(self, kp : KP) -> QPointF:
        rect = self.element.boundingRect()
        return QPointF(kp.value.h * rect.width(), kp.value.v * rect.height())

    def updatePositions(self : Self) -> None:
        rect = self.element.KPRect()
        for kp_loc in self.key_points.keys():
            new_pos = QPointF(
                kp_loc.value.h * rect.width(),
                kp_loc.value.v * rect.height()
            )
            if kp_loc != self.key_points[kp_loc]:
                self.key_points[kp_loc].setPos(new_pos)
        # Also update anchor_offset when size changes
        if self.anchor_loc is not None:
            self.anchor_offset = self.getKeyPointPos(self.anchor_loc)
        self.change.emit()

    def setVisible(self : Self, visible : bool) -> None:
        for kp in self.key_points.values():
            kp.setVisible(visible)
