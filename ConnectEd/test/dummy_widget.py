from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen

class DummyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.GlobalColor.red, 1))
        painter.drawLine(0, 0, self.width(), self.height())
        painter.drawLine(0, self.height(), self.width(), 0)
