from PyQt6.QtWidgets import QMessageBox
from inspect import stack


class ActionsHelpMixin:
    def helpAbout(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])
