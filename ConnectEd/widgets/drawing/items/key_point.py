__all__ = ["KPLoc", "KeyPoint", "KPDef", "KPManager"]

from typing      import Self, Optional
from enum        import Enum
from collections import namedtuple

from PyQt6.QtCore    import Qt, QRectF, QPointF
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, \
                            QWidget, QGraphicsView, QMenu
from PyQt6.QtGui     import QPainter, QPen, QBrush, QPainterPath, QAction

from ....core import SharedContextMenuUtils

from .... import hub


class KPLoc(Enum):
    TOP_LEFT      = (0.0, 0.0)
    TOP_CENTER    = (0.5, 0.0)
    TOP_RIGHT     = (1.0, 0.0)
    CENTER_LEFT   = (0.0, 0.5)
    CENTER        = (0.5, 0.5)
    CENTER_RIGHT  = (1.0, 0.5)
    BOTTOM_LEFT   = (0.0, 1.0)
    BOTTOM_CENTER = (0.5, 1.0)
    BOTTOM_RIGHT  = (1.0, 1.0)

    @property
    def h(self) -> float:
        return self.value[0]

    @property
    def v(self) -> float:
        return self.value[1]

class KeyPoint(QGraphicsItem):
    # class variables
    Z_DELTA = 1
    _MENU = None
    _MENU_ITEM_NAMES = [
        "Assign Anchor"
    ]
    getMenu = SharedContextMenuUtils.getMenu

    # instance variables
    _manager : "KPManager"
    _loc     : KPLoc # parent's key point location
    _grip    : bool
    _cleat   : bool
    _pen     : QPen
    _brush   : QBrush
    _rect    : QRectF
    _rhombus : QPainterPath
    _menu    : QMenu

    def __init__(
        self    : Self,
        manager : "KPManager",
        loc     : KPLoc,
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
        self._pen.setWidth(0)
        self._pen.setStyle(Qt.PenStyle.SolidLine)
        self._brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.onSettingsChange()
        hub.settings.change.connect(self.onSettingsChange)
        self._menu = self.getMenu()

    contextMenuEvent = SharedContextMenuUtils.contextMenuEvent

    def boundingRect(
        self : Self,
        view : Optional[QGraphicsView] = None
    ) -> QRectF:
        return self._rect

    def shape(self : Self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        if self._grip == True or self._manager.anchor == self:
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

    def isMoveable(self : Self) -> bool:
        return self._grip

    def ctxMenuAssignAnchor(self : Self, checked : bool) -> None:
        self._manager.setAnchor(self._loc)

KPDef = namedtuple("KPDef", ["loc", "grip", "cleat"])

class KPManager:
    element       : QGraphicsItem         # parent element
    key_points    : dict[KPLoc, KeyPoint]
    anchor        : Optional[KeyPoint]
    anchor_loc    : Optional[KPLoc]
    anchor_offset : QPointF

    def __init__(
        self    : Self,
        parent  : QGraphicsItem,
        kp_defs : list[KPDef],
        anchor  : Optional[KPLoc] = None
    ) -> None:
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

    def setAnchor(self, anchor : KPLoc) -> None:
        self.anchor = self.key_points[anchor]
        self.anchor_loc = anchor
        self.anchor_offset = self.getKeyPointPos(anchor)
        self.element.update()

    def getKeyPointPos(self, kp : KPLoc) -> QPointF:
        rect = self.element.boundingRect()
        return QPointF(kp.h * rect.width(), kp.v * rect.height())

    def updatePositions(self : Self) -> None:
        self.rect = self.element.KPRect()
        for kp_loc in self.key_points.keys():
            self.key_points[kp_loc].setPos(
                kp_loc.h * self.rect.width(),
                kp_loc.v * self.rect.height()
            )

    def setVisible(self : Self, visible : bool) -> None:
        for kp in self.key_points.values():
            kp.setVisible(visible)
