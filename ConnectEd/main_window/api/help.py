from PyQt6.QtWidgets import QMessageBox

from common import APP_NAME

class MainWindowApiHelpMixin:
    def helpAbout(self):
        QMessageBox.about(self, 'About', f'{APP_NAME}')
