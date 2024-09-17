from PyQt6.QtWidgets import QMessageBox

from app import APP_TITLE


class Actions:
    def __init__(self, parent):
        self.parent = parent

    def fileNew(self):
        QMessageBox.about(self.parent, "TODO", "fileNew")

    def fileOpen(self):
        QMessageBox.about(self.parent, "TODO", "fileOpen")

    def fileSave(self):
        QMessageBox.about(self.parent, "TODO", "fileSave")

    def fileSaveAs(self):
        QMessageBox.about(self.parent, "TODO", "fileSaveAs")

    def fileClose(self):
        QMessageBox.about(self.parent, "TODO", "fileClose")

    def fileExport(self):
        QMessageBox.about(self.parent, "TODO", "fileExport")

    def fileImport(self):
        QMessageBox.about(self.parent, "TODO", "fileImport")

    def filePrint(self):
        QMessageBox.about(self.parent, "TODO", "filePrint")

    def filePrintPreview(self):
        QMessageBox.about(self.parent, "TODO", "filePrintPreview")

    def filePageSetup(self):
        QMessageBox.about(self.parent, "TODO", "filePageSetup")

    def editCancel(self):
        self.parent.canvas.diagram.selectionClear()
        self.parent.canvas.setEditMode(self.parent.canvas.EditMode.FREE)

    def editUndo(self):
        QMessageBox.about(self.parent, "TODO", "editUndo")

    def editRedo(self):
        QMessageBox.about(self.parent, "TODO", "editRedo")

    def editCut(self):
        QMessageBox.about(self.parent, "TODO", "editCut")

    def editCopy(self):
        QMessageBox.about(self.parent, "TODO", "editCopy")

    def editPaste(self):
        QMessageBox.about(self.parent, "TODO", "editPaste")

    def editDelete(self):
        QMessageBox.about(self.parent, "TODO", "editDelete")

    def editSelectAll(self):
        QMessageBox.about(self.parent, "TODO", "editSelectAll")

    def editFind(self):
        QMessageBox.about(self.parent, "TODO", "editFind")

    def editReplace(self):
        QMessageBox.about(self.parent, "TODO", "editReplace")

    def editSelectAll(self):
        QMessageBox.about(self.parent, "TODO", "editSelectAll")

    def editSelectFilter(self):
        QMessageBox.about(self.parent, "TODO", "editSelectFilter")

    def elementBlock(self):
        self.parent.canvas.setEditMode(self.parent.canvas.EditMode.ADD_BLOCK)

    def elementPin(self):
        QMessageBox.about(self.parent, "TODO", "elementPin")

    def elementWire(self):
        QMessageBox.about(self.parent, "TODO", "elementWire")

    def elementTap(self):
        QMessageBox.about(self.parent, "TODO", "elementTap")

    def elementJunction(self):
        QMessageBox.about(self.parent, "TODO", "elementJunction")

    def elementPort(self):
        QMessageBox.about(self.parent, "TODO", "elementPort")

    def elementConnection(self):
        QMessageBox.about(self.parent, "TODO", "elementConnection")

    def elementProperty(self):
        QMessageBox.about(self.parent, "TODO", "elementProperty")

    def elementCode(self):
        QMessageBox.about(self.parent, "TODO", "elementCode")

    def graphicLine(self):
        QMessageBox.about(self.parent, "TODO", "graphicLine")

    def graphicRectangle(self):
        QMessageBox.about(self.parent, "TODO", "graphicRectangle")

    def graphicPolygon(self):
        QMessageBox.about(self.parent, "TODO", "graphicPolygon")

    def graphicArc(self):
        QMessageBox.about(self.parent, "TODO", "graphicArc")

    def graphicEllipse(self):
        QMessageBox.about(self.parent, "TODO", "graphicEllipse")

    def graphicImage(self):
        QMessageBox.about(self.parent, "TODO", "graphicImage")

    def graphicTextLine(self):
        QMessageBox.about(self.parent, "TODO", "graphicTextLine")

    def graphicTextBox(self):
        QMessageBox.about(self.parent, "TODO", "graphicTextBox")

    def viewZoomIn(self):
        self.parent.canvas.zoomIn()

    def viewZoomOut(self):
        self.parent.canvas.zoomOut()

    def viewZoomWindow(self):
        QMessageBox.about(self.parent, "TODO", "viewZoomWindow")

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

    def optionsPreferences(self):
        QMessageBox.about(self.parent, "TODO", "optionsPreferences")

    def helpAbout(self):
        QMessageBox.about(self.parent, "About", APP_TITLE)

