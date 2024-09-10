import sys
from PyQt6.QtCore import Qt, QPoint, QPointF, QSize
from PyQt6.QtGui import QPainter, QPen, QBrush
from PyQt6.QtWidgets import QApplication,QWidget

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
        self.pan          = QPointF(0.0, 0.0) # diagram coordinates
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

    def canvas2diagram(self, point):
        # convert canvas point to diagram point
        r = QPointF(
            (point.x() / self.zoom) + self.pan.x(),
            (point.y() / self.zoom) + self.pan.y()
        )
        return r

    def getKeyboardModifiers(self):
        keyMod = QApplication.queryKeyboardModifiers()
        shift = True if keyMod & Qt.KeyboardModifier.ShiftModifier   else False
        ctrl  = True if keyMod & Qt.KeyboardModifier.ControlModifier else False
        alt   = True if keyMod & Qt.KeyboardModifier.AltModifier     else False
        return shift, ctrl, alt

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
        shift, ctrl, alt = self.getKeyboardModifiers()
        if event.button() == Qt.MouseButton.LeftButton and not shift and not ctrl and not alt:
            d = self.canvas2diagram(event.pos()) # diagram position
            p = snap(d) # snapped diagram position
            self.selectionSet = [] # clear selection set
            for block in self.blocks: # look through diagram objects to see if we clicked on one
                if block.rect.contains(d.toPoint()):
                    self.currentBlock = block
                    self.dragging = True
                    self.startPos = p - block.rect.topLeft()
                    return
            self.startPos = p
            self.currentBlock = diagram.Block(
                self.startPos,
                QSize(10, 10),
                {"reference": "ref?", "value": "val?"} # {"reference": "Referencey?", "value": "value?"}
            )
            self.blocks.append(self.currentBlock)
            self.update()

    def mouseMoveEvent(self, event):
        if self.currentBlock:
            d = self.canvas2diagram(event.pos()) # diagram position
            p = snap(d)
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
        shift, ctrl, alt = self.getKeyboardModifiers()
        match [event.key(), shift, ctrl, alt]:
            case [Qt.Key.Key_I, False, False, False]:
                self.zoom = min(self.zoom * 1.25, prefs.dwg.zoom.max)
                self.update()
            case [Qt.Key.Key_O, False, False, False]:
                self.zoom = max(self.zoom / 1.25, prefs.dwg.zoom.min)
                self.update()
            case [Qt.Key.Key_Left, False, False, False]:
                self.pan.setX(self.pan.x() + prefs.dwg.panStep * self.width() / self.zoom)
                self.update()
            case [Qt.Key.Key_Right, False, False, False]:
                self.pan.setX(self.pan.x() - prefs.dwg.panStep * self.width() / self.zoom)
                self.update()
            case [Qt.Key.Key_Up, False, False, False]:
                self.pan.setY(self.pan.y() + prefs.dwg.panStep * self.height() / self.zoom)
                self.update()
            case [Qt.Key.Key_Down, False, False, False]:
                self.pan.setY(self.pan.y() - prefs.dwg.panStep * self.height() / self.zoom)
                self.update()

    # TODO handle mousewheel event to zoom in/out the canvas