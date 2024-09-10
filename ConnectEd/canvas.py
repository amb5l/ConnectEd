from PyQt6.QtCore import Qt, QPoint, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QBrush, QCursor, QKeySequence
from PyQt6.QtWidgets import QApplication, QWidget
from enum import Enum

from app import prefs
from diagram import diagram

class EditMode(Enum):
    FREE         = 0
    SELECT       = 1
    DRAG         = 2
    ADD_BLOCK    = 3
    ADDING_BLOCK = 4

# snaps from minor to major grid
def snap(position):
    return QPointF(
        int(round(position.x()/10.0, 0) * 10),
        int(round(position.y()/10.0, 0) * 10)
    )

def getModifiers(event):
    shift = True if event.modifiers() & Qt.KeyboardModifier.ShiftModifier   else False
    ctrl  = True if event.modifiers() & Qt.KeyboardModifier.ControlModifier else False
    alt   = True if event.modifiers() & Qt.KeyboardModifier.AltModifier     else False
    return shift, ctrl, alt

class Canvas(QWidget):

    def __init__(self):
        super().__init__()
        self.zoom        = 1.0
        self.pan         = QPointF(0.0, 0.0) # diagram coordinates
        self.startPos    = QPoint() # for dragging etc
        self.editMode    = EditMode.FREE
        self.physicalPos = None

        self.setAutoFillBackground(True)
        self.setMouseTracking(True)

        # set background color to light grey
        p = self.palette()
        p.setColor(self.backgroundRole(), prefs.dwg.color.background)
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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.scale(self.zoom, self.zoom)
        painter.translate(-self.pan)
        visibleRect = QRectF(
            self.canvas2diagram(QPointF(0,0)),
            self.canvas2diagram(QPointF(self.width()-1, self.height()-1))
        )
        # draw background
        painter.fillRect(visibleRect, self.palette().window())
        # draw grid
        # TODO move this to diagram.py ?
        if prefs.dwg.grid.enable:
            gridRect = QRectF(
                visibleRect.topLeft() - QPointF(prefs.edit.grid.x, prefs.edit.grid.y),
                visibleRect.bottomRight() + QPointF(prefs.edit.grid.x, prefs.edit.grid.y)
            )
            x1 = int(gridRect.left() / prefs.edit.grid.x) * prefs.edit.grid.x
            x2 = int(gridRect.right() / prefs.edit.grid.x) * prefs.edit.grid.x
            y1 = int(gridRect.top() / prefs.edit.grid.y) * prefs.edit.grid.y
            y2 = int(gridRect.bottom() / prefs.edit.grid.y) * prefs.edit.grid.y
            pen = QPen(prefs.dwg.grid.lineColor, prefs.dwg.grid.lineWidth, Qt.PenStyle.SolidLine)
            brush = QBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(pen)
            painter.setBrush(brush)
            for x in range(x1, x2, prefs.edit.grid.x):
                painter.drawLine(x, y1, x, y2)
            for y in range(y1, y2, prefs.edit.grid.y):
                painter.drawLine(x1, y, x2, y)
        # draw (visible portion of) diagram
        diagram.draw(painter, visibleRect)

    def mousePressEvent(self, event):
        shift, ctrl, alt = getModifiers(event)
        if event.button() == Qt.MouseButton.LeftButton and not shift and not ctrl and not alt:
            pos = self.canvas2diagram(event.pos()) # diagram position
            match self.editMode:
                case EditMode.FREE:
                    self.startPos = snap(pos)
                    diagram.selectionClear() # clear selection set on unmodified click
                    if (object := diagram.click(pos)) is not None:
                        diagram.selectionAdd(object)
                    diagram.selectionStart(pos)
                    self.update()
                    self.editMode = EditMode.SELECT
                    return
                case EditMode.ADD_BLOCK:
                    diagram.newBlockStart(snap(pos))
                    self.update()
                    self.editMode = EditMode.ADDING_BLOCK
                case EditMode.ADDING_BLOCK:
                    diagram.newBlockFinish()
                    self.update()
                    self.editMode = EditMode.ADD_BLOCK
                case _:
                    pass

    def mouseMoveEvent(self, event):
        self.physicalPos = event.pos()
        pos = self.canvas2diagram(event.pos()) # diagram position
        match self.editMode:
            case EditMode.SELECT:
                diagram.selectionResize(pos)
                self.update()
            case EditMode.ADDING_BLOCK:
                diagram.newBlockResize(snap(pos))
                self.update()
            case _:
                pass

    def mouseReleaseEvent(self, event):
        pos = self.canvas2diagram(event.pos()) # diagram position
        if event.button() == Qt.MouseButton.LeftButton:
            match self.editMode:
                case EditMode.SELECT:
                    diagram.selectionEnd()
                    self.update()
                    self.editMode = EditMode.FREE
                case EditMode.ADDING_BLOCK:
                    if snap(pos) != diagram.startPos:
                        diagram.newBlockFinish()
                        self.update()
                        self.editMode = EditMode.ADD_BLOCK

    def keyPressEvent(self, event):
        key = event.key()
        shift, ctrl, alt = getModifiers(event)
        match [key, shift, ctrl, alt]:
            case prefs.kbd.escape:
                if self.editMode != EditMode.FREE:
                    self.editMode = EditMode.FREE
                else:
                    diagram.selectionClear()
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
                self.update()
            case prefs.kbd.addBlock:
                self.editMode = EditMode.ADD_BLOCK
                self.setCursor(QCursor(Qt.CursorShape.CrossCursor)) # mouse pointer signifies add block mode
                self.update()
            case prefs.kbd.zoomIn:
                z1 = self.zoom
                z2 = min(self.zoom * 1.25, prefs.dwg.zoom.max)
                dz = (1/z1) - (1/z2)
                self.pan.setX(self.pan.x() + (self.physicalPos.x() * dz))
                self.pan.setY(self.pan.y() + (self.physicalPos.y() * dz))
                self.zoom = z2
                self.update()
            case prefs.kbd.zoomOut:
                z1 = self.zoom
                z2 = max(self.zoom / 1.25, prefs.dwg.zoom.min)
                dz = (1/z1) - (1/z2)
                self.pan.setX(self.pan.x() + (self.physicalPos.x() * dz))
                self.pan.setY(self.pan.y() + (self.physicalPos.y() * dz))
                self.zoom = z2
                self.update()
            case prefs.kbd.zoomFull:
                self.zoom = min(
                    self.width()  / diagram.extents.width(),
                    self.height() / diagram.extents.height()
                )
                self.pan = QPointF(0.0, 0.0)
                self.update()
            case prefs.kbd.panLeft:
                self.pan.setX(self.pan.x() - prefs.dwg.panStep * self.width() / self.zoom)
                self.update()
            case prefs.kbd.panRight:
                self.pan.setX(self.pan.x() + prefs.dwg.panStep * self.width() / self.zoom)
                self.update()
            case prefs.kbd.panUp:
                self.pan.setY(self.pan.y() - prefs.dwg.panStep * self.height() / self.zoom)
                self.update()
            case prefs.kbd.panDown:
                self.pan.setY(self.pan.y() + prefs.dwg.panStep * self.height() / self.zoom)
                self.update()

    # TODO handle mousewheel event to zoom in/out the canvas