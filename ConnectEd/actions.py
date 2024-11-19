from inspect import stack
from PyQt6.QtWidgets import QMessageBox

from app import APP_TITLE

def _actions_todo():
    caller_frame = stack()[1]
    caller_function_name = caller_frame.function
    caller_parent = caller_frame.frame.f_locals['self'].parent
    QMessageBox.about(caller_parent, "TODO", caller_function_name)

class Actions:
    def __init__(self, parent):
        self.parent = parent

    def fileNew(self):
        _actions_todo()

    def fileOpen(self):
        _actions_todo()

    def fileSave(self):
        _actions_todo()

    def fileSaveAs(self):
        _actions_todo()

    def fileClose(self):
        _actions_todo()

    def fileExport(self):
        _actions_todo()

    def fileImport(self):
        _actions_todo()

    def filePrint(self):
        _actions_todo()

    def filePrintPreview(self):
        _actions_todo()

    def filePageSetup(self):
        _actions_todo()

    def editCancel(self):
        self.parent.canvas.diagram.selectionClear()
        self.parent.canvas.setEditMode(self.parent.canvas.EditMode.FREE)

    def editUndo(self):
        _actions_todo()

    def editRedo(self):
        _actions_todo()

    def editCut(self):
        _actions_todo()

    def editCopy(self):
        _actions_todo()

    def editPaste(self):
        _actions_todo()

    def editDelete(self):
        _actions_todo()

    def editSelectAll(self):
        _actions_todo()

    def editFind(self):
        _actions_todo()

    def editReplace(self):
        _actions_todo()

    def editSelectAll(self):
        _actions_todo()

    def editSelectFilter(self):
        _actions_todo()

    def elementBlock(self):
        self.parent.canvas.setEditMode(self.parent.canvas.EditMode.ADD_BLOCK)

    def elementPin(self):
        _actions_todo()

    def elementWire(self):
        _actions_todo()

    def elementTap(self):
        _actions_todo()

    def elementJunction(self):
        _actions_todo()

    def elementPort(self):
        _actions_todo()

    def elementConnection(self):
        _actions_todo()

    def elementProperty(self):
        _actions_todo()

    def elementCode(self):
        _actions_todo()

    def graphicLine(self):
        _actions_todo()
        #_actions_todo()

    def graphicRectangle(self):
        _actions_todo()

    def graphicPolygon(self):
        _actions_todo()

    def graphicArc(self):
        _actions_todo()

    def graphicEllipse(self):
        _actions_todo()

    def graphicImage(self):
        _actions_todo()

    def graphicTextLine(self):
        _actions_todo()

    def graphicTextBox(self):
        _actions_todo()

    def viewZoomIn(self):
        self.parent.canvas.zoomIn()

    def viewZoomOut(self):
        self.parent.canvas.zoomOut()

    def viewZoomWindow(self):
        _actions_todo()

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
        _actions_todo()

    def helpAbout(self):
        QMessageBox.about(self.parent, "About", APP_TITLE)

