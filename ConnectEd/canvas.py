import sys
from PyQt6.QtCore import Qt, QRect, QPoint, QPointF, QSize
from PyQt6.QtGui import QPainter, QPen, QBrush
from PyQt6.QtWidgets import QWidget

from app import prefs
import diagram


# snaps from minor to major grid
def snap(position):
    return QPoint(
        int(round(position.x()/10.0, 0) * 10),
        int(round(position.y()/10.0, 0) * 10)
    )

class Canvas(QWidget):

    def __init__(self):
        super().__init__()
        self.zoom         = 1.0
        self.pan          = QPointF(0.0, 0.0)
        self.blocks       = []
        self.currentBlock = None
        self.dragging     = False
        self.startPos     = QPoint()
        self.setAutoFillBackground(True)

        # set background color to light grey
        p = self.palette()
        p.setColor(self.backgroundRole(), prefs.dwg.background)
        self.setPalette(p)

        # Set focus policy to accept key input
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.scale(self.zoom, self.zoom)
        painter.translate(self.pan)
        # draw background
        painter.fillRect(self.rect(), self.palette().window())
        # draw grid
        pen = QPen(prefs.dwg.grid.lineColor, prefs.dwg.grid.lineWidth, Qt.PenStyle.SolidLine)
        brush = QBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(pen)
        painter.setBrush(brush)
        for x in range(0, self.width(), prefs.dwg.grid.x):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), prefs.dwg.grid.y):
            painter.drawLine(0, y, self.width(), y)
        # draw blocks
        pen = QPen(prefs.dwg.block.lineColor, prefs.dwg.block.lineWidth, Qt.PenStyle.SolidLine)
        if prefs.dwg.block.fillColor == None:
            brush = QBrush(Qt.BrushStyle.NoBrush)
        else:
            brush = QBrush(prefs.dwg.block.fillColor)
        painter.setPen(pen)
        painter.setBrush(brush)
        for block in self.blocks:
            block.draw(painter)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            p = snap(event.pos())
            for block in self.blocks:
                if block.rect.contains(event.pos()):
                    self.currentBlock = block
                    self.dragging = True
                    self.startPos = p - block.rect.topLeft()
                    return
            self.startPos = p
            self.currentBlock = diagram.Block(
                self.startPos,
                QSize(10, 10),
                {"prop1": "val1", "prop2": "val2"} # {"reference": "Referencey?", "value": "value?"}
            )
            self.blocks.append(self.currentBlock)
            self.update()

    def mouseMoveEvent(self, event):
        if self.currentBlock:
            p = snap(event.pos())
            if self.dragging:
                self.currentBlock.setPosition(p - self.startPos)
            else:
                if p.x() > self.startPos.x() and p.y() > self.startPos.y():                                # current pos is right and below
                    self.currentBlock.setSize(QSize(p.x() - self.startPos.x(), p.y() - self.startPos.y()))
                elif p.x() > self.startPos.x() and p.y() <= self.startPos.y():                             # current pos is right and above
                    self.currentBlock.setSize(QSize(p.x() - self.startPos.x(), self.startPos.y() - p.y()))
                    self.currentBlock.setPosition(QPoint(self.startPos.x(), p.y()))
                elif p.x() <= self.startPos.x() and p.y() <= self.startPos.y():                            # current pos is left and above
                    self.currentBlock.setSize(QSize(self.startPos.x() - p.x(), self.startPos.y() - p.y()))
                    self.currentBlock.setPosition(p)
                elif p.x() <= self.startPos.x() and p.y() > self.startPos.y():                             # current pos is left and below
                    self.currentBlock.setSize(QSize(self.startPos.x() - p.x(), p.y() - self.startPos.y()))
                    self.currentBlock.setPosition(QPoint(p.x(), self.startPos.y()))
                elif p == self.startPos:                                                                   # current pos is same as start pos
                    self.currentBlock.setSize(QSize(10, 10))                                               # set minimum size
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.currentBlock = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Insert:
            # Add a new block at the center of the canvas
            center = self.rect().center()
            new_block = QRect(center.x() - 50, center.y() - 50, 100, 100)
            self.blocks.append(new_block)
            self.update()
        elif event.key() == Qt.Key.Key_I:
            self.zoom += 0.25
            self.update()
        elif event.key() == Qt.Key.Key_O:
            self.zoom -= 0.25
            self.update()
        elif event.key() == Qt.Key.Key_Left:
            self.pan.setX(self.pan.x() + 100.0)
            self.update()
        elif event.key() == Qt.Key.Key_Right:
            self.pan.setX(self.pan.x() - 100.0)
            self.update()
        elif event.key() == Qt.Key.Key_Up:
            self.pan.setY(self.pan.y() + 100.0)
            self.update()
        elif event.key() == Qt.Key.Key_Down:
            self.pan.setY(self.pan.y() - 100.0)
            self.update()


    # TODO handle mousewheel event to zoom in/out the canvas