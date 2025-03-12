from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PyQt6.QtGui     import QPainter, QPen, QBrush, QPolygonF, QPainterPath

from ...core import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import KeyPoint


class Grip(QGraphicsItem):
    Z_DELTA = 1

    key_point : 'KeyPoint'
    prev_pos  : QPointF

    def __init__(
        self      : 'Grip',
        parent    : 'QGraphicsItem',
        key_point : 'KeyPoint'
    ) -> None:
        super().__init__(parent)
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsMovable              , True )
        self.setFlag( f.ItemSendsGeometryChanges   , True )
        self.setFlag( f.ItemIgnoresTransformations , True )
        self.setZValue(self.parentItem().zValue() + self.Z_DELTA)
        self.key_point = key_point
        self.prev_pos  = self.pos()

    def boundingRect(self) -> QRectF:
        size = settings.prefs.display.items.selected.grip.size
        rect = QRectF(-size/2, -size/2, size, size)
        offset = QPointF(
            self.parentItem().anchor.value.h * self.parentItem().rect().width(),
            self.parentItem().anchor.value.v * self.parentItem().rect().height()
        )
        rect.translate(-offset)
        return rect

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def paint(
        self    : 'Grip',
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        is_anchor = self == self.parentItem().grips[self.parentItem().anchor]
        theme = settings.theme.anchor if is_anchor else settings.theme.grip
        painter.setPen(QPen(theme.line, 0, Qt.PenStyle.SolidLine))
        painter.setBrush(QBrush(theme.fill, Qt.BrushStyle.SolidPattern))
        painter.drawRect(self.boundingRect())

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            delta = value - self.prev_pos
            self.parentItem().gripResize(self.key_point, delta)
            self.prev_pos = value
            return value
        elif change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.prev_pos = self.pos()
        return super().itemChange(change, value)
