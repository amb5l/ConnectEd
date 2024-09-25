from PyQt6.QtWidgets import QMessageBox
from inspect import stack


class ActionsViewMixin:
    def fileNew(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def fileOpen(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def fileSave(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def fileSaveAs(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def fileClose(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def fileExportVHDL(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def fileExportVerilog(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def fileExportPDF(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def fileExportSVG(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def fileImportVHDL(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def fileImportVerilog(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])
