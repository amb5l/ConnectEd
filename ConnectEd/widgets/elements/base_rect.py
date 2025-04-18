__all__ = ['BaseRectangle']

from typing import Union

from PyQt6.QtCore import Qt, QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QGraphicsRectItem, QStyleOptionGraphicsItem, QWidget
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QBrush

from . import \
    Element, ElementXmlMixin, \
    KeyPoint, PenSpec, BrushSpec, TextSpec, \
    Grip

from ... import hub


class BaseRectangle(QGraphicsRectItem, Element, ElementXmlMixin):
    """Base class for rectangle items."""
    XML_ATTRIBUTES = {
        'anchor'     : 'KeyPoint',
        'pen_spec'   : 'PenSpec',
        'brush_spec' : 'BrushSpec',
        'text_spec'  : 'TextSpec'
    }
    XML_PROPERTIES = {
        'pos'  : ( 'QPointF' , lambda self, value: self.setPos(value)  , lambda self: self.pos()         ),
        'size' : ( 'QSizeF'  ,  lambda self, value: self.setSize(value) , lambda self: self.rect().size() )
    }
    MIN_SIZE = QSizeF(1.0, 1.0)

    anchor : KeyPoint
    grips  : dict[KeyPoint, Grip]

    def __init__(
        self,
        pos        : QPointF = QPointF(0, 0),
        size       : QSizeF = QSizeF(0, 0),
        anchor     : KeyPoint = KeyPoint.TOP_LEFT,
        pen_spec   : Union[ bool, PenSpec   ] = True,
        brush_spec : Union[ bool, BrushSpec ] = True,
        text_spec  : Union[ bool, TextSpec  ] = False
    ) -> None:
        QGraphicsRectItem.__init__(self)
        Element.__init__(self, pen_spec, brush_spec, text_spec)
        self.grips = {p: Grip(self, p) for p in KeyPoint if p != KeyPoint.CENTER}
        self.anchor = anchor
        self.setPosSize(pos, size)
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        self.setZValue(self.Z)
        self.setAnchor(anchor)
        self.updateGripsPosition()
        self.updateGripsVisibility()
        self.updateGripsZValue()

    def setSize(self, size : QSizeF) -> None:
        self.setRect(0, 0, size.width(), size.height())

    def getSize(self) -> QSizeF:
        return self.rect().size()

    def setAnchor(self, anchor : KeyPoint = KeyPoint.TOP_LEFT) -> None:
        self.anchor = anchor

    def getAnchor(self) -> KeyPoint:
        return self.anchor

    def setPosSize(self, pos : QPointF, size : QSizeF) -> None:
        self.setPos(pos)
        if size.width() < self.MIN_SIZE.width():
            size.setWidth(self.MIN_SIZE.width())
        if size.height() < self.MIN_SIZE.height():
            size.setHeight(self.MIN_SIZE.height())
        self.setRect(0, 0, size.width(), size.height())
        self.updateGripsPosition()

    def setPoints(self, p1_or_x1, p2_or_y1=None, x2=None, y2=None) -> None:
        if p2_or_y1 is not None and x2 is not None and y2 is not None:
            p1, p2 = QPointF(p1_or_x1, p2_or_y1), QPointF(x2, y2)
        else:
            p1, p2 = p1_or_x1, p2_or_y1
        rect = QRectF(p1, p2).normalized()
        self.setPosSize(rect.topLeft(), rect.size())

    def getPoints(self) -> tuple[QPointF, QPointF]:
        return self.pos(), self.pos() + self.rect().bottomRight()

    def updateGripsPosition(self) -> None:
        for kp in self.grips.keys():
            self.grips[kp].setPos(
                kp.value.h * self.rect().width(),
                kp.value.v * self.rect().height()
            )

    def updateGripsVisibility(self) -> None:
        for grip in self.grips.values():
            grip.setVisible(
                self.isSelected() and len(self.scene().selectedItems()) == 1
            )

    def updateGripsZValue(self) -> None:
        for grip in self.grips.values():
            grip.setZValue(self.zValue() + Grip.Z_DELTA)

    def gripResize(self, kp : KeyPoint, delta : QPointF) -> None:
        p1, p2 = self.getPoints()
        d = delta
        match kp:
            case KeyPoint.TOP_LEFT:
                self.setPoints(p1 + d, p2)
            case KeyPoint.TOP_CENTER:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x(), p2.y())
            case KeyPoint.TOP_RIGHT:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x() + d.x(), p2.y())
            case KeyPoint.CENTER_LEFT:
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y())
            case KeyPoint.CENTER_RIGHT:
                self.setPoints(p1.x(), p1.y(), p2.x() + d.x(), p2.y())
            case KeyPoint.BOTTOM_LEFT:
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y() + d.y())
            case KeyPoint.BOTTOM_CENTER:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x(), p2.y())
            case KeyPoint.BOTTOM_RIGHT:
                self.setPoints(p1, p2 + d)
            case _:
                raise ValueError(f'Invalid key point: {kp}')

    def rect(self) -> QRectF:
        rect = super().rect()
        rect.translate(
            -self.anchor.value.h * rect.width(),
            -self.anchor.value.v * rect.height()
        )
        return rect

    def boundingRect(self) -> QRectF:
        w = max(
            self.penWidth(),
            hub.settings.prefs.display.elements.selected.grip.size
        )
        return self.rect().adjusted(-w/2, -w/2, w/2, w/2)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def paint(
        self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        pen = self.penFromSpec()
        painter.setPen(pen)
        brush = self.brushFromSpec()
        painter.setBrush(brush)
        painter.drawRect(QRectF(
            -self.rect().width() * self.anchor.value.h,
            -self.rect().height() * self.anchor.value.v,
            self.rect().width(),
            self.rect().height()
        ))

    def itemChange(self, change, value):
        if change == self.GraphicsItemChange.ItemSelectedHasChanged:
            self.updateGripsVisibility()
        return super().itemChange(change, value)