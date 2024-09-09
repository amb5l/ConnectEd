from PyQt6.QtCore import Qt, QRect, QPoint, QSize, pyqtSignal
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPen, QBrush
from enum import Enum
import app

class RectAnchorPoint(Enum):
    CENTER       = 0
    TOPLEFT      = 1
    TOPCENTER    = 2
    TOPRIGHT     = 3
    RIGHTCENTER  = 4
    BOTTOMRIGHT  = 5
    BOTTOMCENTER = 6
    BOTTOMLEFT   = 7
    LEFTCENTER   = 8

class PropertyVisibility(Enum):
    NONE  = 0
    VALUE = 1
    BOTH  = 2

# a clickable QLabel
class InteractiveText(QLabel):
    def __init__(self,content):
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

# InteractiveText with various attributes
class PropertyText(InteractiveText):
    def __init__(self, name, value, position, size, anchor, rotation = 0, visibility=PropertyVisibility.VALUE):
        match visibility:
            case PropertyVisibility.VALUE:
                text = value
            case PropertyVisibility.BOTH:
                text = name + "=" + value
            case _:
                text = ""
        super().__init__(text)
        self.position   = position   # QPoint (w.r.t parent object anchor point)
        self.size       = size       # bounding rectangle QSize
        self.anchor     = anchor     # RectAnchorPoint
        self.rotation   = rotation   # int
        self.visibility = visibility # bool

    def draw(self, painter):
        if self.visibility == PropertyVisibility.NONE:
            return
        painter.setFont(app.preferences.fonts.blockProperty)
        pen = QPen(app.preferences.colors.blockProperty)
        painter.setPen(pen)
        if not self.rotation:
            painter.save()
            painter.rotate(self.rotation)
        painter.drawText(self.anchor, super().text)
        if not self.rotation:
            painter.restore()

class Block:
    rect = QRect()
    def __init__(self, position, size, properties):
        self.position   = position
        self.size       = size
        self.properties = {}
        n = 0
        for name, value in properties.items():
            if n == 0:
                prop_position = self.rect.topLeft()
                prop_anchor = RectAnchorPoint.BOTTOMLEFT
            else:
                prop_position = self.rect.bottomLeft()
                prop_anchor = RectAnchorPoint.TOPLEFT + QPoint(0, 10*n)
            self.properties[name] = PropertyText(
                name,
                value,
                prop_position,
                QSize(100, 10),
                prop_anchor,
                0,
                PropertyVisibility.BOTH
            )
            n += 1

    def setSize(self, size):
        self.rect.setSize(size)

    def setPosition(self, position):
        self.rect.moveTo(position)

    def draw(self,painter):
        pen = QPen(app.preferences.colors.blockOutline, 1, Qt.PenStyle.SolidLine)
        brush = QBrush(app.preferences.colors.blockFill)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self.rect)
        for _, v in self.properties.values():
            v.draw(painter)
