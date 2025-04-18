__all__ = ['BaseText']

from typing import Self, Union

from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsTextItem, QStyleOptionGraphicsItem, QWidget
from PyQt6.QtGui import QPainter, QPainterPath

from . import Element, KeyPoint, PenSpec, BrushSpec, TextSpec


class BaseText(QGraphicsTextItem, Element):
    """Base class for text items."""
    XML_ATTRIBUTES = {
        'text'       : ( 'str'       , lambda self, value: self.setText      (value) , lambda self: self.getText      () ),
        'pos'        : ( 'QPointF'   , lambda self, value: self.setPos       (value) , lambda self: self.getPos       () ),
        'anchor'     : ( 'KeyPoint'  , lambda self, value: self.setAnchor    (value) , lambda self: self.getAnchor    () ),
        'pen_spec'   : ( 'PenSpec'   , lambda self, value: self.setPenSpec   (value) , lambda self: self.getPenSpec   () ),
        'brush_spec' : ( 'BrushSpec' , lambda self, value: self.setBrushSpec (value) , lambda self: self.getBrushSpec () ),
        'text_spec'  : ( 'TextSpec'  , lambda self, value: self.setTextSpec  (value) , lambda self: self.getTextSpec  () )
    }

    anchor : KeyPoint

    def __init__(
        self       : Self,
        text       : str = '',
        pos        : QPointF = QPointF(0, 0),
        anchor     : KeyPoint = KeyPoint.TOP_LEFT,
        pen_spec   : Union[ bool, PenSpec   ] = False,
        brush_spec : Union[ bool, BrushSpec ] = False,
        text_spec  : Union[ bool, TextSpec  ] = True
    ) -> None:
        QGraphicsTextItem.__init__(self, text)
        Element.__init__(self, pen_spec, brush_spec, text_spec)
        self.setPos(pos)
        self.setZValue(self.Z)
        self.setAnchor(anchor)
        self.setTextSpec()

    def setAnchor(self : Self, anchor : KeyPoint = KeyPoint.TOP_LEFT) -> None:
        self.anchor = anchor

    def boundingRect(self : Self) -> QRectF:
        rect = super().boundingRect()
        return QRectF(
            -rect.width() * self.anchor.value.h,
            -rect.height() * self.anchor.value.v,
            rect.width(), rect.height()
        )

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
        self.fontFromSpec()
        self.setFont(self.font)
        rect = self.anchoredBoundingRect()
        painter.translate(rect.topLeft())
        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
            self.toPlainText()
        )
