# ConnectEd/slots/file.py

from PyQt6.QtCore import QFile, QFileInfo, QIODevice
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from common import logger, APP_NAME
from settings import prefs


class DiagramSlotsFileMixin:
    @slot
    def fileNew(self):
        # TODO check for modified, save if so?
        # prompt user for new file name
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setNameFilter('ConnectEd Diagrams (*.ced)')
        dialog.setDefaultSuffix('ced')
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_name = dialog.getSaveFileName(self.window, 'Create New File')
        # create new empty file
        file = QFile(file_name)
        if not file.open(QIODevice.OpenModeFlag.WriteOnly):
            QMessageBox.critical(None, 'Error', f'Failed to open file {file_name} for writing')
            return
        info = QFileInfo(file)
        file.close()
        # initialise empty diagram
        self.data.modified = True
        self.data.title    = info.baseName()
        self.data.size     = prefs.file.new.size
        self.data.margin   = prefs.file.new.margin
        self.data.content  = []
        self.data.wip      = []
        # update actions
        self.window.commands.update()

    def fileOpen(self):
        # prompt user for file path/name
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter('ConnectEd Diagrams (*.ced)')
        dialog.setDefaultSuffix('ced')
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        file_name = dialog.getOpenFileName(self.window, 'Open File')
        # open file
        file = QFile(file_name)
        if not file.open(QIODevice.OpenModeFlag.ReadOnly):
            QMessageBox.critical(None, 'Error', f'Failed to open file {file_name} for reading')
            return
        # read file
        self.loadXml(file)
        # close file
        file.close()
        # update actions
        self.window.commands.update()

    def fileSave(self):
        # prompt user to confirm file name
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter('ConnectEd Diagrams (*.ced)')
        dialog.setDefaultSuffix('ced')
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_name = dialog.getSaveFileName(self.window, 'Save File')
        # open file
        file = QFile(file_name)
        if not file.open(QIODevice.OpenModeFlag.WriteOnly):
            QMessageBox.critical(None, 'Error', f'Failed to open file {file_name} for writing')
            return
        # write file
        self.saveXml(file)
        file.close()
        # mark diagram unmodified
        self.data.modified = False
        # update actions
        self.window.commands.update()

    def fileSaveAs(self):
        # prompt user for file path/name
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setNameFilter('ConnectEd Diagrams (*.ced)')
        dialog.setDefaultSuffix('ced')
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_name = dialog.getSaveFileName(self.window, 'Save File As')
        # create new empty file
        file = QFile(file_name)
        if not file.open(QIODevice.OpenModeFlag.WriteOnly):
            QMessageBox.critical(None, 'Error', f'Failed to open file {file_name} for writing')
            return
        # write file
        self.saveXml(file)
        file.close()
        # mark diagram unmodified
        self.data.modified = False
        # update actions
        self.window.commands.update()

    def fileClose(self):
        self.window.todo()
        # clear diagram data
        self.data = None
        # update actions
        self.window.commands.update()
