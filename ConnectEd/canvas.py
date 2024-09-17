from PyQt6.QtCore import Qt, QPoint, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QBrush, QCursor, QColor
from PyQt6.QtWidgets import QWidget
from enum import Enum

from prefs import prefs

class Canvas(QWidget):
    def __init__(self, diagram):
        super().__init__()
        self.diagram           = diagram
        self.zoom              = 1.0
        self.pan               = QPointF(0.0, 0.0)
        self.initialResizeDone = False
        self.startPos          = QPoint() # for dragging etc
        self.editMode          = self.EditMode.FREE
        self.physicalPos       = QPoint(0, 0) # TODO initialize from current mouse position

        self.setAutoFillBackground(True)
        self.setMouseTracking(True)

        # set background color to light grey
        p = self.palette()
        p.setColor(self.backgroundRole(), prefs.dwg.background)
        self.setPalette(p)

        # uncomment to enable keypress events
        #self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def resizeEvent(self, event):
        if not self.initialResizeDone:
            self.zoomFull()
            self.initialResizeDone = True

    class EditMode(Enum):
        FREE         = 0
        SELECT       = 1
        DRAG         = 2
        ADD_BLOCK    = 3
        ADDING_BLOCK = 4

    def EditModeText(self, mode):
        match mode:
            case self.EditMode.FREE:         t = "Ready"
            case self.EditMode.SELECT:       t = "Release to complete selection box"
            case self.EditMode.DRAG:         t = "Drag"
            case self.EditMode.ADD_BLOCK:    t = "Click to create block"
            case self.EditMode.ADDING_BLOCK: t = "Click to complete block"
            case _:                          t = "UNKNOWN EDIT MODE"
        self.parent().statusBar.showMessage(t)

    # snaps from minor to major grid
    def snap(self, position):
        return QPointF(
            int(round(position.x()/10.0, 0) * 10),
            int(round(position.y()/10.0, 0) * 10)
        )

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
        painter.save()
        # draw background
        painter.fillRect(self.visibleRect, self.palette().window())
        # draw grid
        if prefs.edit.grid.enable:
            x1 = int( self.gridRect.left()   / prefs.edit.grid.size.width()  )
            y1 = int( self.gridRect.top()    / prefs.edit.grid.size.height() )
            x2 = int( self.gridRect.right()  / prefs.edit.grid.size.width()  )
            y2 = int( self.gridRect.bottom() / prefs.edit.grid.size.height() )
            pen = QPen(prefs.dwg.grid.line.color, prefs.dwg.grid.line.width, Qt.PenStyle.SolidLine)
            brush = QBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(pen)
            painter.setBrush(brush)
            for x in range(x1, x2+1):
                painter.drawLine(
                    QPointF(x  * prefs.edit.grid.size.width(), y1 * prefs.edit.grid.size.height()),
                    QPointF(x  * prefs.edit.grid.size.width(), y2 * prefs.edit.grid.size.height())
                )
            for y in range(y1, y2+1):
                painter.drawLine(
                    QPointF(x1 * prefs.edit.grid.size.width(), y  * prefs.edit.grid.size.height()),
                    QPointF(x2 * prefs.edit.grid.size.width(), y  * prefs.edit.grid.size.height())
                )
        # draw border round visible canvas (debug)
        pen = QPen(QColor(255,0,0), 0, Qt.PenStyle.SolidLine)
        brush = QBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(QRectF(
            self.canvas2diagram(QPointF(0, 0)),
            self.canvas2diagram(QPointF(self.width()-1, self.height()-1))
            #QPointF(
            #    -prefs.view.zoomFullMargin.left(),
            #    -prefs.view.zoomFullMargin.top()
            #),
            #QPointF(
            #    self.width(),
            #    self.height()
            #)
        ))
        # draw (visible portion of) diagram
        painter.restore()
        self.diagram.draw(painter, self.visibleRect)

    #-------------------------------------------------------------------------------
    # zoom and pan

    def zoomFull(self):
        self.zoom = min(
            self.width()  / ( self.diagram.extents.width()  + prefs.view.zoomFullMargin.left() + prefs.view.zoomFullMargin.right()  ),
            self.height() / ( self.diagram.extents.height() + prefs.view.zoomFullMargin.top()  + prefs.view.zoomFullMargin.bottom() )
        )
        self.pan = QPointF(-prefs.view.zoomFullMargin.left(), -prefs.view.zoomFullMargin.top())
        self.zoomPanFinish()

    def zoomIn(self,n=1):
        z1 = self.zoom
        z2 = min(self.zoom * (1.25**n), prefs.view.zoomLimits.max)
        dz = (1/z1) - (1/z2)
        self.pan.setX(self.pan.x() + (self.physicalPos.x() * dz))
        self.pan.setY(self.pan.y() + (self.physicalPos.y() * dz))
        self.zoom = z2
        self.zoomPanFinish()

    def zoomOut(self, n=1):
        z1 = self.zoom
        z2 = max(self.zoom / (1.25**n), prefs.view.zoomLimits.min)
        dz = (1/z1) - (1/z2)
        self.pan.setX(self.pan.x() + (self.physicalPos.x() * dz))
        self.pan.setY(self.pan.y() + (self.physicalPos.y() * dz))
        self.zoom = z2
        self.zoomPanFinish()

    def panLeft(self):
        self.pan.setX(self.pan.x() - prefs.dwg.panStep * self.width() / self.zoom)
        self.zoomPanFinish()

    def panRight(self):
        self.pan.setX(self.pan.x() + prefs.dwg.panStep * self.width() / self.zoom)
        self.zoomPanFinish()

    def panUp(self):
        self.pan.setY(self.pan.y() - prefs.dwg.panStep * self.height() / self.zoom)
        self.zoomPanFinish()

    def panDown(self):
        self.pan.setY(self.pan.y() + prefs.dwg.panStep * self.height() / self.zoom)
        self.zoomPanFinish()

    def zoomPanFinish(self):
        self.visibleRect = QRectF(
            self.canvas2diagram(QPointF(0, 0)),
            self.canvas2diagram(QPointF(self.width()-1, self.height()-1))
        )
        self.gridRect = QRectF(
            self.visibleRect.topLeft()     - QPointF(prefs.edit.grid.size.width(), prefs.edit.grid.size.height()),
            self.visibleRect.bottomRight() + QPointF(prefs.edit.grid.size.width(), prefs.edit.grid.size.height())
        )
        self.update()

    #-------------------------------------------------------------------------------

    def setEditMode(self, mode):
        self.editMode = mode
        self.EditModeText(mode)
        match mode:
            case self.EditMode.ADD_BLOCK:
                self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            case _:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    #-------------------------------------------------------------------------------
    # mouse related

    def mousePressEvent(self, event):
        shift, ctrl, alt = self.getModifiers(event)
        if event.button() == Qt.MouseButton.LeftButton and not shift and not ctrl and not alt:
            pos = self.canvas2diagram(event.pos()) # diagram position
            match self.editMode:
                case self.EditMode.FREE:
                    self.startPos = self.snap(pos)
                    self.diagram.selectionClear() # clear selection set on unmodified click
                    if (object := self.diagram.click(pos)) is not None:
                        self.diagram.selectionAdd(object)
                    self.diagram.selectionStart(pos)
                    self.update()
                    self.setEditMode(self.EditMode.SELECT)
                    return
                case self.EditMode.ADD_BLOCK:
                    self.diagram.newBlockStart(self.snap(pos))
                    self.update()
                    self.setEditMode(self.EditMode.ADDING_BLOCK)
                case self.EditMode.ADDING_BLOCK:
                    self.diagram.newBlockFinish()
                    self.update()
                    self.setEditMode(self.EditMode.ADD_BLOCK)
                case _:
                    pass

    def mouseMoveEvent(self, event):
        self.physicalPos = event.pos()
        pos = self.canvas2diagram(event.pos()) # diagram position
        match self.editMode:
            case self.EditMode.SELECT:
                self.diagram.selectionResize(pos)
                self.update()
            case self.EditMode.ADDING_BLOCK:
                self.diagram.newBlockResize(self.snap(pos))
                self.update()
            case _:
                pass

    def mouseReleaseEvent(self, event):
        pos = self.canvas2diagram(event.pos()) # diagram position
        if event.button() == Qt.MouseButton.LeftButton:
            match self.editMode:
                case self.EditMode.SELECT:
                    self.diagram.selectionEnd()
                    self.update()
                    self.setEditMode(self.EditMode.FREE)
                case self.EditMode.ADDING_BLOCK:
                    if self.snap(pos) != self.diagram.startPos:
                        self.diagram.newBlockFinish()
                        self.update()
                        self.setEditMode(self.EditMode.ADD_BLOCK)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()/prefs.view.wheelStep
        print("wheelEvent", delta)
        if delta > 0:
            self.zoomIn(delta)
        elif delta < 0:
            self.zoomOut(-delta)

    #-------------------------------------------------------------------------------
    # keyboard related

    def getModifiers(self, event):
        shift = True if event.modifiers() & Qt.KeyboardModifier.ShiftModifier   else False
        ctrl  = True if event.modifiers() & Qt.KeyboardModifier.ControlModifier else False
        alt   = True if event.modifiers() & Qt.KeyboardModifier.AltModifier     else False
        return shift, ctrl, alt

    #-------------------------------------------------------------------------------

    #def keyPressEvent(self, event):
    #    key = event.key()
    #    shift, ctrl, alt = getModifiers(event)
    #    match [key, shift, ctrl, alt]:
    #        case prefs.kbd.escape:
    #            if self.editMode != EditMode.FREE:
    #                self.editMode = EditMode.FREE
    #            else:
    #                self.diagram.selectionClear()
    #            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
    #            self.update()
    #        case prefs.kbd.addBlock:
    #            self.editMode = EditMode.ADD_BLOCK
    #            self.setCursor(QCursor(Qt.CursorShape.CrossCursor)) # mouse pointer signifies add block mode
    #            self.update()
