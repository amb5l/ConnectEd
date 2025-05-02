__all__ = ["BaseRectangle"]

from typing import Self, Optional, Any

from PyQt6.QtCore    import QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QGraphicsRectItem, QStyleOptionGraphicsItem, QWidget
from PyQt6.QtGui     import QPainter, QPainterPath, QUndoCommand

from . import ElementWithAnchor, KPLoc, PenSpec, BrushSpec, ResizeGrip, \
              cmdPlaceElement

from .... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class BaseRectangle(QGraphicsRectItem, ElementWithAnchor):
    """Base class for rectangle elements."""
    XML_ATTRS = ElementWithAnchor.XML_ATTRS | {
        "size" : (
            "QSizeF",
            lambda self, value: self.setSize(value),
            lambda self: self.rect().size()
        )
    }
    GRIP_TYPE = ResizeGrip
    GRIP_POINTS = [kp for kp in KPLoc if kp != KPLoc.CENTER]
    MIN_SIZE = QSizeF(1.0, 1.0)

    anchor : KPLoc
    grips  : dict[KPLoc, ResizeGrip]

    def __init__(
        self       : Self,
        pos        : QPointF = QPointF(0, 0),
        size_or_p2 : QSizeF | QPointF = QSizeF(0, 0),
        anchor     : KPLoc = KPLoc.TOP_LEFT,
        pen_spec   : bool | PenSpec   = True,
        brush_spec : bool | BrushSpec = True
    ) -> None:
        QGraphicsRectItem.__init__(self)
        ElementWithAnchor.__init__(self, anchor, pen_spec, brush_spec)
        if isinstance(size_or_p2, QSizeF):
            self.setPosSize(pos, size_or_p2)
        else:
            self.setPoints(pos, size_or_p2)
        self.updateGripsPosition()
        self.updateGripsVisibility()

    def setSize(self : Self, size : QSizeF) -> None:
        self.setRect(0, 0, size.width(), size.height())

    def setPosSize(self : Self, pos : QPointF, size : QSizeF) -> None:
        self.setPos(pos)
        if size.width() < self.MIN_SIZE.width():
            size.setWidth(self.MIN_SIZE.width())
        if size.height() < self.MIN_SIZE.height():
            size.setHeight(self.MIN_SIZE.height())
        self.setRect(0, 0, size.width(), size.height())
        self.updateGripsPosition()

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

    def updateGripsPosition(self : Self) -> None:
        for kp in self.grips.keys():
            self.grips[kp].setPos(
                kp.h * self.rect().width(),
                kp.v * self.rect().height()
            )

    def updateGripsVisibility(self : Self) -> None:
        for grip in self.grips.values():
            grip.setVisible(
                self.isSelected() and len(self.scene().selectedItems()) == 1
            )

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

    def rect(self : Self) -> QRectF:
        rect = super().rect()
        rect.translate(
            -self.anchor.h * rect.width(),
            -self.anchor.v * rect.height()
        )
        return rect

    gripsRect = rect

    def boundingRect(self : Self) -> QRectF:
        w = max(
            self.penWidth(),
            hub.settings.prefs.display.elements.key_point.size
        )
        return self.rect().adjusted(-w/2, -w/2, w/2, w/2)

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
        pen = self.penFromLineSpec()
        painter.setPen(pen)
        brush = self.brushFromSpec()
        painter.setBrush(brush)
        painter.drawRect(QRectF(
            -self.rect().width() * self.anchor.h,
            -self.rect().height() * self.anchor.v,
            self.rect().width(),
            self.rect().height()
        ))

    def itemChange(
        self   : Self,
        change : QGraphicsRectItem.GraphicsItemChange,
        value  : Any
    ) -> None:
        if change == self.GraphicsItemChange.ItemSelectedHasChanged:
            self.updateGripsVisibility()
        return QGraphicsRectItem.itemChange(self,change, value)

class cmdPlaceBaseRectangle(cmdPlaceElement):
    element    : BaseRectangle
    pos        : QPointF
    size_or_p2 : QSizeF | QPointF
    anchor     : KPLoc

    def __init__(
        self       : Self,
        scene      : Optional["DrawingScene"] = None,
        element    : Optional[BaseRectangle] = None,
        pos        : QPointF = QPointF(0, 0),
        size_or_p2 : QSizeF | QPointF = QSizeF(0, 0),
        anchor     : KPLoc = KPLoc.TOP_LEFT,
        pen_spec   : bool | PenSpec   = True,
        brush_spec : bool | BrushSpec = True,
        wip        : bool = False
    ):
        super().__init__(scene, element, pen_spec, brush_spec, False, wip)
        self.pos        = pos
        self.size_or_p2 = size_or_p2
        self.anchor     = anchor
        self.element.setAnchor(self.anchor)
        self.element.setPosSizeOrP2(self.pos, self.size_or_p2)

    def mergeWith(self : Self, other: QUndoCommand) -> bool:
        if not super().mergeWith(other):
            return False
        self.pos        = other.pos
        self.size_or_p2 = other.size_or_p2
        self.anchor     = other.anchor
        self.element.setAnchor(self.anchor)
        self.element.setPosSizeOrP2(self.pos, self.size_or_p2)
        return True

    def redo(self : Self):
        super().redo()
        self.element.setAnchor(self.anchor)
        self.element.setPosSizeOrP2(self.pos, self.size_or_p2)
