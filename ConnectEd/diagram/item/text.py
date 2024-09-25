from enum import Enum
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPen, QBrush, QFont

from prefs import prefs
from diagram_common import getRectAnchorOffset, getRectAnchorPoint

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
