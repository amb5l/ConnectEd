from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMdiSubWindow

class SubWindow(QMdiSubWindow):
    def __init__(self, parent=None):
        super(SubWindow, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
