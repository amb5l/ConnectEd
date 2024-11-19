from PyQt6.QtWidgets import QMessageBox
from inspect import stack


class ActionsOptionsMixin:
    def optionsDiagram(self):
        # sheet size, border/margin, title block enable
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def optionsThemes(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def optionsPreference(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def optionsShortcuts(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def optionsReset(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])
