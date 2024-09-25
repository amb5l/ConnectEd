from PyQt6.QtWidgets import QMessageBox
from inspect import stack


class ActionsViewMixin:
    def viewGrid(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def viewTransparent(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def viewOpaque(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def viewZoomIn(self):
        self.parent.canvas.zoomIn()

    def viewZoomOut(self):
        self.parent.canvas.zoomOut()

    def viewZoomWindow(self):
        self.parent.canvas.setState(self.parent.canvas.State.ZOOM)

    def viewZoomFull(self):
        self.parent.canvas.zoomFull()

    def viewPanLeft(self):
        self.parent.canvas.panLeft()

    def viewPanRight(self):
        self.parent.canvas.panRight()

    def viewPanUp(self):
        self.parent.canvas.panUp()

    def viewPanDown(self):
        self.parent.canvas.panDown()