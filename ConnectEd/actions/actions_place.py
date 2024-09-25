from PyQt6.QtWidgets import QMessageBox
from inspect import stack


class ActionsPlaceMixin:
    def placeBlock(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def placePin(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def placeWire(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def placeTap(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def placeJunction(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def placePort(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def placeCode(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def placeLine(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def placeRectangle(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def placePolygon(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def placeArc(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def placeEllipse(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def placeTextline(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def placeTextbox(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def placeImage(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])
