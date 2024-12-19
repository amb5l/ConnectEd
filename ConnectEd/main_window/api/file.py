from PyQt6.QtWidgets import QFileDialog, QMessageBox

from common     import logger
from misc       import createInst, getInst, normAbsPath
from sub_window import SubWindow
from canvas     import Canvas
from diagram    import Diagram


class MainWindowApiFileMixin:
    def fileNew(self):
        diagram = createInst(Diagram)
        diagram.fileNew()
        sub_window = createInst(SubWindow)
        canvas = Canvas(self, sub_window, diagram)
        sub_window.setWidget(canvas)
        canvas.setParent(sub_window)
        self.mdi_area.addSubWindow(sub_window)
        sub_window.showMaximized()

    def fileOpen(self, path=None):
        # prompt user for file path/name if not provided
        if path is None:
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
            dialog.setNameFilter('ConnectEd Diagrams (*.ced)')
            dialog.setDefaultSuffix('ced')
            dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
            path = dialog.getOpenFileName(self, 'Open File')
        # normalise path
        path = normAbsPath(path)
        # check if file is already open
        sub_windows = self.mdi_area.subWindowList()
        canvases = [sub_window.widget() for sub_window in sub_windows]
        diagrams = [canvas.diagram for canvas in canvases if isinstance(canvas, Canvas)]
        if path in [diagram.path for diagram in diagrams]:
            logger.error(f'file {path} is already open')
            QMessageBox.critical(self, 'Error', f'File {path} is already open')
            return
        # open file
        diagram = Diagram()
        if diagram.fileOpen(path):
            self.diagrams.append(diagram)
            canvas = Canvas(diagram)
            sub_window = self.mdi_area.addSubWindow(canvas)
            sub_window.showMaximised()

    def fileSave(self, diagram=None):
        if diagram is None:
            sub_window = getInst(self.mdi_area.activeSubWindow(), SubWindow)
            canvas = getInst(sub_window.widget(), Canvas)
            diagram = getInst(canvas.diagram, Diagram)
        if diagram.data.path is None:
            self.fileSaveAs(diagram)
        else:
            diagram.fileSave()

    def fileSaveAs(self, diagram=None):
        if diagram is None:
            # get active diagram
            sub_window = getInst(self.mdi_area.activeSubWindow(), SubWindow)
            canvas = getInst(sub_window.widget(), Canvas)
            diagram = getInst(canvas.diagram, Diagram)
        # prompt user for file path/name
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setNameFilter('ConnectEd Diagrams (*.ced)')
        dialog.setDefaultSuffix('ced')
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        path = normAbsPath(dialog.getSaveFileName(self.window, 'Save File'))
        # update diagram path
        diagram.data.path = path
        # save diagram
        diagram.fileSave()

    def fileClose(self):
        sub_window = getInst(self.mdi_area.activeSubWindow(), SubWindow)
        canvas = getInst(sub_window.widget(), Canvas)
        diagram = getInst(canvas.diagram, Diagram)
        if diagram.data.modified:
            self.fileSave(diagram)
        # TODO verify that this deletes the underlying canvas and diagram
        if sub_window.close():
            self.diagrams.remove(diagram)
        else:
            logger.error('MDI subwindow close failed')
            QMessageBox.critical(self, 'Error', 'Unable to close MDI subwindow')
