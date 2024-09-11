from PyQt6.QtWidgets import QMessageBox

from app import APP_TITLE


class Actions:
    def fileNew(self, h):
        QMessageBox.about(h, "TODO", "fileNew")

    def fileOpen(self, h):
        QMessageBox.about(h, "TODO", "fileOpen")

    def fileSave(self, h):
        QMessageBox.about(h, "TODO", "fileSave")

    def fileSaveAs(self, h):
        QMessageBox.about(h, "TODO", "fileSaveAs")

    def fileClose(self, h):
        QMessageBox.about(h, "TODO", "fileClose")

    def fileExport(self, h):
        QMessageBox.about(h, "TODO", "fileExport")

    def fileImport(self, h):
        QMessageBox.about(h, "TODO", "fileImport")

    def filePrint(self, h):
        QMessageBox.about(h, "TODO", "filePrint")

    def filePrintPreview(self, h):
        QMessageBox.about(h, "TODO", "filePrintPreview")

    def filePageSetup(self, h):
        QMessageBox.about(h, "TODO", "filePageSetup")

    def editCancel(self, h):
        h.canvas.setEditMode(h.canvas.EditMode.FREE)

    def editUndo(self, h):
        QMessageBox.about(h, "TODO", "editUndo")

    def editRedo(self, h):
        QMessageBox.about(h, "TODO", "editRedo")

    def editCut(self, h):
        QMessageBox.about(h, "TODO", "editCut")

    def editCopy(self, h):
        QMessageBox.about(h, "TODO", "editCopy")

    def editPaste(self, h):
        QMessageBox.about(h, "TODO", "editPaste")

    def editDelete(self, h):
        QMessageBox.about(h, "TODO", "editDelete")

    def editSelectAll(self, h):
        QMessageBox.about(h, "TODO", "editSelectAll")

    def editFind(self, h):
        QMessageBox.about(h, "TODO", "editFind")

    def editReplace(self, h):
        QMessageBox.about(h, "TODO", "editReplace")

    def editSelectAll(self, h):
        QMessageBox.about(h, "TODO", "editSelectAll")

    def editSelectFilter(self, h):
        QMessageBox.about(h, "TODO", "editSelectFilter")

    def elementBlock(self, h):
        h.canvas.setEditMode(h.canvas.EditMode.ADD_BLOCK)
        #QMessageBox.about(h, "TODO", "elementBlock")

    def elementPin(self, h):
        QMessageBox.about(h, "TODO", "elementPin")

    def elementWire(self, h):
        QMessageBox.about(h, "TODO", "elementWire")

    def elementTap(self, h):
        QMessageBox.about(h, "TODO", "elementTap")

    def elementJunction(self, h):
        QMessageBox.about(h, "TODO", "elementJunction")

    def elementPort(self, h):
        QMessageBox.about(h, "TODO", "elementPort")

    def elementConnection(self, h):
        QMessageBox.about(h, "TODO", "elementConnection")

    def elementProperty(self, h):
        QMessageBox.about(h, "TODO", "elementProperty")

    def elementCode(self, h):
        QMessageBox.about(h, "TODO", "elementCode")

    def graphicLine(self, h):
        QMessageBox.about(h, "TODO", "graphicLine")

    def graphicRectangle(self, h):
        QMessageBox.about(h, "TODO", "graphicRectangle")

    def graphicPolygon(self, h):
        QMessageBox.about(h, "TODO", "graphicPolygon")

    def graphicArc(self, h):
        QMessageBox.about(h, "TODO", "graphicArc")

    def graphicEllipse(self, h):
        QMessageBox.about(h, "TODO", "graphicEllipse")

    def graphicImage(self, h):
        QMessageBox.about(h, "TODO", "graphicImage")

    def graphicTextLine(self, h):
        QMessageBox.about(h, "TODO", "graphicTextLine")

    def graphicTextBox(self, h):
        QMessageBox.about(h, "TODO", "graphicTextBox")

    def viewZoomIn(self, h):
        h.canvas.zoomIn()

    def viewZoomOut(self, h):
        h.canvas.zoomOut()

    def viewZoomWindow(self, h):
        QMessageBox.about(h, "TODO", "viewZoomWindow")

    def viewZoomFull(self, h):
        h.canvas.zoomFull()

    def viewPanLeft(self, h):
        h.canvas.panLeft()

    def viewPanRight(self, h):
        h.canvas.panRight()

    def viewPanUp(self, h):
        h.canvas.panUp()

    def viewPanDown(self, h):
        h.canvas.panDown()

    def optionsPreferences(self, h):
        QMessageBox.about(h, "TODO", "optionsPreferences")

    def helpAbout(self, h):
        QMessageBox.about(h, "About", APP_TITLE)

actions = Actions()
