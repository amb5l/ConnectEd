from PyQt6.QtCore import Qt, QPoint, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QBrush, QCursor
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

class Canvas(QWidget):

    def __init__(self):
        super().__init__()
        self.zoom         = 1.0
        self.pan          = QPointF(0.0, 0.0) # diagram coordinates
        self.startPos     = QPoint() # for dragging etc
        self.editMode     = EditMode.FREE

        self.setAutoFillBackground(True)

        # set background color to light grey
        p = self.palette()
        p.setColor(self.backgroundRole(), prefs.dwg.backgroundColor)
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
        painter.translate(-self.pan)
        visibleRect = QRectF(
            self.canvas2diagram(QPointF(0,0)),
            self.canvas2diagram(QPointF(self.width()-1, self.height()-1))
        )
        # draw background
        painter.fillRect(visibleRect, self.palette().window())
        # draw grid
        # TODO move this to diagram.py ?
        gridRect = QRectF(
            visibleRect.topLeft() - QPointF(prefs.dwg.grid.x, prefs.dwg.grid.y),
            visibleRect.bottomRight() + QPointF(prefs.dwg.grid.x, prefs.dwg.grid.y)
        )
        x1 = int(gridRect.left() / prefs.dwg.grid.x) * prefs.dwg.grid.x
        x2 = int(gridRect.right() / prefs.dwg.grid.x) * prefs.dwg.grid.x
        y1 = int(gridRect.top() / prefs.dwg.grid.y) * prefs.dwg.grid.y
        y2 = int(gridRect.bottom() / prefs.dwg.grid.y) * prefs.dwg.grid.y
        pen = QPen(prefs.dwg.grid.lineColor, prefs.dwg.grid.lineWidth, Qt.PenStyle.SolidLine)
        brush = QBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(pen)
        painter.setBrush(brush)
        for x in range(x1, x2, prefs.dwg.grid.x):
            painter.drawLine(x, y1, x, y2)
        for y in range(y1, y2, prefs.dwg.grid.y):
            painter.drawLine(x1, y, x2, y)
        # draw (visible portion of) diagram
        diagram.draw(painter, visibleRect)

    def mousePressEvent(self, event):
        shift, ctrl, alt = self.getKeyboardModifiers()
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
        shift, ctrl, alt = self.getKeyboardModifiers()
        match [event.key(), shift, ctrl, alt]:
            case [Qt.Key.Key_Escape, False, False, False]:
                self.editMode = EditMode.FREE
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
                self.update()
            case [Qt.Key.Key_Insert, False, False, False]:
                self.editMode = EditMode.ADD_BLOCK
                self.setCursor(QCursor(Qt.CursorShape.CrossCursor)) # mouse pointer signifies add block mode
                self.update()
            case [Qt.Key.Key_I, False, False, False]:
                self.zoom = min(self.zoom * 1.25, prefs.dwg.zoom.max)
                self.update()
            case [Qt.Key.Key_O, False, False, False]:
                self.zoom = max(self.zoom / 1.25, prefs.dwg.zoom.min)
                self.update()
            case [Qt.Key.Key_Left, False, False, False]:
                self.pan.setX(self.pan.x() - prefs.dwg.panStep * self.width() / self.zoom)
                self.update()
            case [Qt.Key.Key_Right, False, False, False]:
                self.pan.setX(self.pan.x() + prefs.dwg.panStep * self.width() / self.zoom)
                self.update()
            case [Qt.Key.Key_Up, False, False, False]:
                self.pan.setY(self.pan.y() - prefs.dwg.panStep * self.height() / self.zoom)
                self.update()
            case [Qt.Key.Key_Down, False, False, False]:
                self.pan.setY(self.pan.y() + prefs.dwg.panStep * self.height() / self.zoom)
                self.update()

    # TODO handle mousewheel event to zoom in/out the canvas