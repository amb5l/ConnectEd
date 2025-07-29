__all__ = ["KPLoc", "KPReverse", "KPDef", "KeyPoint"]

from typing      import Self, Optional
from enum        import Enum
from dataclasses import dataclass

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, \
                            QWidget, QGraphicsView
from PyQt6.QtGui     import QPainter, QPainterPath

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import ElementKeypointsMixin
    from .grip import Grip


@dataclass(frozen=True)
class KPLoc:
    name : str
    h    : float
    v    : float

class KPLoc(Enum):
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
    "Top Left"      : KPLoc.TOP_LEFT,
    "Top Center"    : KPLoc.TOP_CENTER,
    "Top Right"     : KPLoc.TOP_RIGHT,
    "Center Left"   : KPLoc.CENTER_LEFT,
    "Center"        : KPLoc.CENTER,
    "Center Right"  : KPLoc.CENTER_RIGHT,
    "Bottom Left"   : KPLoc.BOTTOM_LEFT,
    "Bottom Center" : KPLoc.BOTTOM_CENTER,
    "Bottom Right"  : KPLoc.BOTTOM_RIGHT
}

@dataclass
class KPDef:
    """KeyPoint Definition"""
    loc    : KPLoc  # location
    resize : bool   # whether the key point can be used for resize
    cleat  : bool   # whether the key point can be a cleat

class KeyPoint(QGraphicsItem):
    # instance variables
    _loc    : KPLoc         # location of key point in parent
    _resize : bool          # whether the key point can be used for resize
    _brect  : QRectF        # bounding rect
    _hshape : QPainterPath  # shape for hit detection
    grip    : "Grip"        # associated (child) grip

    def __init__(
        self    : Self,
        parent  : "ElementKeypointsMixin",
        loc     : KPLoc,
        resize  : bool
    ) -> None:
        super().__init__(parent)
        self.setZValue(parent.zValue())
        self.setFlag( self.GraphicsItemFlag.ItemHasNoContents , True  )
        self.setFlag( self.GraphicsItemFlag.ItemIsMovable     , False )
        self.setFlag( self.GraphicsItemFlag.ItemIsSelectable  , False )
        self.setFlag( self.GraphicsItemFlag.ItemIsFocusable   , False )
        self._loc = loc
        self._resize = resize
        self._brect = QRectF()
        self._hshape = QPainterPath()
        self._hshape.addRect(self._brect)
        from .grip import Grip
        self.grip = Grip(self)

    def mousePressEvent(self, event):
        event.ignore()
        return

    def mouseMoveEvent(self, event):
        event.ignore()
        return

    def mouseReleaseEvent(self, event):
        event.ignore()
        return

    def mouseDoubleClickEvent(self, event):
        event.ignore()
        return

    def contextMenuEvent(self, event):
        event.ignore()
        return

    def onAnchorChange(self : Self, anchor : bool) -> None:
        self.grip.onAnchorChange(anchor)

    def getLoc(self : Self) -> KPLoc:
        return self._loc

    #def moveBy(self : Self, dx : float, dy : float) -> None:
    #    parent_element = self.parentItem()
    #    parent_element.moveKeypoint(self._loc, QPointF(dx, dy))

    def boundingRect(self : Self) -> QRectF:
        return self._brect

    def shape(self : Self) -> QPainterPath:
        return self._hshape

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        pass

