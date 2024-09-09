from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QRect, QPoint, QPointF

# canvas states:
# adding_block
# dragging_block

class Canvas(QWidget):

    def __init__(self):
        super().__init__()
        self.zoom = 1.0
        self.pan = QPointF(0.0, 0.0)
        self.blocks = []
        self.current_block = None
        self.dragging = False
        self.drag_offset = QPoint()
        self.setAutoFillBackground(True)

        # set background color to light grey
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(8, 8, 8))
        self.setPalette(p)

        # Set focus policy to accept key input
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.scale(self.zoom, self.zoom)
        painter.translate(self.pan)
        # draw background
        painter.fillRect(self.rect(), self.palette().window())
        # draw grid (within sheet extent)
        # adjust grid according to zoom level
        pen = QPen(QColor(16, 16, 16), 1, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        grid_size = 20
        for x in range(0, self.width(), grid_size):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), grid_size):
            painter.drawLine(0, y, self.width(), y)
        # draw blocks
        pen = QPen(QColor(128, 128, 128))
        painter.setPen(pen)
        for block in self.blocks:
            painter.drawRect(block)
            painter.drawText(block.topLeft(), "Blocky")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            for block in self.blocks:
                if block.contains(event.pos()):
                    self.current_block = block
                    self.dragging = True
                    self.drag_offset = event.pos() - block.topLeft()
                    return
            self.current_block = QRect(event.pos(), event.pos())
            self.blocks.append(self.current_block)
            self.update()

    def mouseMoveEvent(self, event):
        if self.dragging and self.current_block:
            self.current_block.moveTopLeft(event.pos() - self.drag_offset)
            self.update()
        elif self.current_block:
            self.current_block.setBottomRight(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.current_block = None

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