from PyQt6.QtCore    import Qt, QPointF, QRectF, QXmlStreamWriter
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PyQt6.QtGui     import QPainter, QPen, QBrush, QPainterPath

from ... import hub

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
        self.key_point = key_point
        self.prev_pos  = self.pos()

    def parentPos(self) -> QPointF:
        return self.parentItem().pos() + self.pos()

    def boundingRect(self) -> QRectF:
        size = hub.settings.prefs.display.elements.selected.grip.size
        return QRectF(-size/2, -size/2, size, size)

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
        a = self == self.parentItem().grips[self.parentItem().anchor]
        theme = hub.settings.theme.anchor if a else hub.settings.theme.grip
        painter.setPen(QPen(theme.line, 0, Qt.PenStyle.SolidLine))
        painter.setBrush(QBrush(theme.fill, Qt.BrushStyle.SolidPattern))
        painter.drawRect(self.boundingRect())

    def toXml(self : 'Grip', xw : QXmlStreamWriter) -> None:
        pass
