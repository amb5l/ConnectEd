__all__ = ["BaseRectangle"]

from typing      import Self, Optional, overload

from PyQt6.QtCore    import QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QGraphicsRectItem, QStyleOptionGraphicsItem, \
                            QWidget, QMenu
from PyQt6.QtGui     import QPainter, QPainterPath, QUndoCommand

from ....core   import SharedContextMenuUtils

from ...dialogs import FillDialog

from . import Element, KPLoc, KPDef, KPManager, cmdPlaceElement

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class BaseRectangle(QGraphicsRectItem, Element):
    """Base class for rectangle elements."""
    XML_ATTRS = Element.XML_ATTRS | {
        "size" : (
            "QSizeF",
            lambda self, value: self.setSize(value),
            lambda self: self.rect().size()
        )
    }
    MIN_SIZE = QSizeF(1.0, 1.0)
    _MENU = None
    _MENU_ITEM_NAMES = [
        "Fill..."
    ]
    getMenu = SharedContextMenuUtils.getMenu

    _kpm           : KPManager
    _rect          : QRectF
    _bounding_rect : QRectF
    _shape         : QPainterPath
    _menu          : QMenu

    def __init__(
        self              : Self,
        rect_or_pos_or_ax : QRectF | QPointF | float = QRectF(),
        size_or_p2_or_ay  : Optional[QSizeF | QPointF | float] = None,
        w                 : Optional[float] = None,
        h                 : Optional[float] = None
    ) -> None:
        QGraphicsRectItem.__init__(self)
        Element.__init__(self, has_line=True, has_fill=True)
        self._kpm = KPManager(self, [KPDef(k, True, False) for k in KPLoc])
        self._shape = QPainterPath()
        if isinstance(rect_or_pos_or_ax, QRectF):
            self.setRect(rect_or_pos_or_ax)
        elif isinstance(rect_or_pos_or_ax, float):
            self.setRect(rect_or_pos_or_ax, size_or_p2_or_ay, w, h)
        elif isinstance(rect_or_pos_or_ax, QPointF):
            if isinstance(size_or_p2_or_ay, QSizeF):
                self.setPosSize(rect_or_pos_or_ax, size_or_p2_or_ay)
            else:
                self.setPoints(rect_or_pos_or_ax, size_or_p2_or_ay)
        # TODO error case
        self._menu = self.getMenu()

    contextMenuEvent = SharedContextMenuUtils.contextMenuEvent

    def setRect(
        self       : Self,
        rect_or_ax : Optional[QRectF | float | int] = None,
        ay         : Optional[float | int]          = None,
        w          : Optional[float | int]          = None,
        h          : Optional[float | int]          = None
    ) -> None:
        # TODO handle minimum size
        if isinstance(rect_or_ax, QRectF):
            super().setRect(rect_or_ax)
        else:
            super().setRect(rect_or_ax, ay, w, h)
        self._rect = self.rect()
        w = self.appearance.line.pen.widthF()
        self._bounding_rect = self._rect.adjusted(-w/2, -w/2, w/2, w/2)
        self._shape.clear()
        self._shape.addRect(self._bounding_rect)
        self._kpm.updatePositions()

    def boundingRect(self : Self) -> QRectF:
        return self._bounding_rect

    def shape(self : Self) -> QPainterPath:
        return self._shape

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        painter.setPen(self.appearance.line.pen)
        painter.setBrush(self.appearance.fill.brush)
        painter.drawRect(self._rect)

    def KPRect(self : Self) -> QRectF:
        return self._rect

    def setKPVisible(self : Self, visible : bool) -> None:
        self._kpm.setVisible(visible)

    def setSize(self : Self, size : QSizeF) -> None:
        self.setRect(0, 0, size.width(), size.height())

    def setPosSize(self : Self, pos : QPointF, size : QSizeF) -> None:
        self.setPos(pos)
        size.setWidth(max(size.width(), self.MIN_SIZE.width()))
        size.setHeight(max(size.height(), self.MIN_SIZE.height()))
        self.setRect(0, 0, size.width(), size.height())

    def setPoints(
        self     : Self,
        p1_or_x1 : QPointF | float,
        p2_or_y1 : QPointF | float | None = None,
        x2       : float | None = None,
        y2       : float | None = None
    ) -> None:
        if p2_or_y1 is not None and x2 is not None and y2 is not None:
            p1, p2 = QPointF(p1_or_x1, p2_or_y1), QPointF(x2, y2)
        else:
            p1, p2 = p1_or_x1, p2_or_y1
        rect = QRectF(p1, p2).normalized()
        self.setPosSize(rect.topLeft(), rect.size())

    def setPosSizeOrP2(
        self       : Self,
        pos        : QPointF,
        size_or_p2 : QSizeF | QPointF
    ) -> None:
        if isinstance(size_or_p2, QSizeF):
            self.setPosSize(pos, size_or_p2)
        else:
            self.setPoints(pos, size_or_p2)

    def getPoints(self : Self) -> tuple[QPointF, QPointF]:
        return self.pos(), self.pos() + self.rect().bottomRight()

    def moveKeyPoint(self : Self, kp : KPLoc, delta : QPointF) -> None:
        p1, p2 = self.getPoints()
        d = delta
        match kp:
            case KPLoc.TOP_LEFT:
                self.setPoints(p1 + d, p2)
            case KPLoc.TOP_CENTER:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x(), p2.y())
            case KPLoc.TOP_RIGHT:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x() + d.x(), p2.y())
            case KPLoc.CENTER_LEFT:
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y())
            case KPLoc.CENTER:
                self.setPos(self.pos() + d)
            case KPLoc.CENTER_RIGHT:
                self.setPoints(p1.x(), p1.y(), p2.x() + d.x(), p2.y())
            case KPLoc.BOTTOM_LEFT:
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y() + d.y())
            case KPLoc.BOTTOM_CENTER:
                self.setPoints(p1.x(), p1.y(), p2.x(), p2.y() + d.y())
            case KPLoc.BOTTOM_RIGHT:
                self.setPoints(p1, p2 + d)
            case _:
                raise ValueError(f"Invalid key point: {kp}")

    def ctxMenuFill(self : Self, checked: bool) -> None:
        dialog = FillDialog(
            current_color = self.appearance.fill.getColor(),
            default_color = self.appearance.fill.getDefaults().color,
            current_style = self.appearance.fill.getStyle(),
            default_style = self.appearance.fill.getDefaults().style
        )
        if dialog.exec():
            self.appearance.fill.setColor(dialog.getColor())
            self.appearance.fill.setStyle(dialog.getStyle())
            self.update()

def placeBaseRectangle(
    scene             : "DrawingScene",
    rect_or_pos_or_ax : QRectF | QPointF | float,
    size_or_ay        : Optional[QSizeF | float] = None,
    w                 : Optional[float]          = None,
    h                 : Optional[float]          = None
) -> None:
    scene.addItem(BaseRectangle(rect_or_pos_or_ax, size_or_ay, w, h))

class cmdPlaceBaseRectangle(cmdPlaceElement):
    element    : BaseRectangle
    pos        : QPointF
    size_or_p2 : QSizeF | QPointF

    def __init__(
        self       : Self,
        scene      : Optional["DrawingScene"] = None,
        element    : Optional[BaseRectangle] = None,
        pos        : QPointF = QPointF(0, 0),
        size_or_p2 : QSizeF | QPointF = QSizeF(0, 0)
    ):
        super().__init__(scene, element)
        self.pos = pos
        self.size_or_p2 = size_or_p2

    def mergeWith(self : Self, other: QUndoCommand) -> bool:
        if not super().mergeWith(other):
            return False
        self.pos        = other.pos
        self.size_or_p2 = other.size_or_p2
        return True

    def redo(self : Self):
        super().redo()
        self.element.setPosSizeOrP2(self.pos, self.size_or_p2)
        self.element.update()