from enum import Enum
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPen, QBrush

from prefs import prefs
from .common import getRectAnchorOffset, getRectAnchorPoint

#-------------------------------------------------------------------------------
# single line of text

class TextLine(QLabel):
    def __init__(self, content=""):
        super().__init__(content)
        super().setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard) # focus policy = Qt::ClickFocus
        self.mousePressed = False
        self.clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.mousePressed = True

    def mouseReleaseEvent(self, event):
        self.mousePressed = False
        self.clicked.emit()

    def leaveEvent(self, event):
        self.mousePressed = False
        return super().leaveEvent(event)

#-------------------------------------------------------------------------------
# Property (name = value)

class PropertyVisibility(Enum):
    NONE  = 0
    VALUE = 1
    BOTH  = 2

class Property(TextLine):
    def __init__(
        self,
        parent,
        name,
        value,
        anchor,
        rotation = 0.0,
        visibility=PropertyVisibility.VALUE
    ):
        super().__init__()
        self.parent       = parent       # e.g. Block
        self.name         = name
        self.value        = value
        self.anchor       = anchor       # e.g. BlockPropertyAnchor
        self.rotation     = rotation     # int
        self.visibility   = visibility   # bool
        self.boundingRect = None
        self.selected     = False
        self.highlighted  = False

    def selectPoint(self, p):
        if self.boundingRect is None:
            return False
        elif self.boundingRect.contains(p):
            self.selected = True
            return True # signifies hit, no need to consider other objects
        return False

    def selectTogglePoint(self, p):
        if self.boundingRect is None:
            return False
        elif self.boundingRect.contains(p):
            self.selected = not self.selected
            return True # signifies hit, no need to consider other objects
        return False

    def selectRect(self, r):
        if self.boundingRect is None:
            return
        elif prefs.edit.select.enclose and r.contains(self.boundingRect):
            self.selected = True
        elif r.intersects(self.boundingRect):
            self.selected = True
        return

    def deselect(self):
        self.selected = False

    def draw(self, painter):
        match self.visibility:
            case PropertyVisibility.NONE:
                return
            case PropertyVisibility.VALUE:
                text = self.value
            case PropertyVisibility.BOTH:
                text = self.name + "=" + self.value
        painter.save()
        pen = QPen(prefs.dwg.block.property.color, 0.0, Qt.PenStyle.SolidLine)
        brush = QBrush(prefs.dwg.block.property.color)
        if self.highlighted:
            pen.setColor(prefs.dwg.highlighted)
            brush.setColor(prefs.dwg.highlighted)
        elif self.selected:
            pen.setColor(prefs.dwg.selected)
            brush.setColor(prefs.dwg.selected)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.setFont(prefs.dwg.block.property.font)
        flags = Qt.TextFlag.TextSingleLine
        if self.boundingRect == None:
            self.boundingRect = painter.boundingRect(QRectF(0,0,1,1), flags, text)
        position = getRectAnchorPoint(self.parent.rect, self.anchor.remote) + \
                   self.anchor.offset - \
                   getRectAnchorOffset(self.boundingRect, self.anchor.local)
        painter.rotate(-self.rotation)
        painter.translate(position)
        painter.drawText(self.boundingRect, flags, text)
        if prefs.dwg.block.property.line is not None:
            pen = QPen(prefs.dwg.block.property.line.color, prefs.dwg.block.property.line.width, Qt.PenStyle.SolidLine)
            brush = QBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(pen)
            painter.setBrush(brush)
            painter.drawRect(self.boundingRect)
        painter.restore()
