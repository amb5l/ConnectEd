from PyQt6.QtGui import QPaintEvent
from PyQt6.QtWidgets import QStatusBar, QLabel

class StatusBar(QStatusBar):

    def __init__(self, parent):
        super().__init__(parent)

        self.xy     = QLabel("(?, ?)")
        self.zoom   = QLabel("??? %")
        self.select = QLabel("0 items selected")
        self.msg    = QLabel("Initializing...")
        self.addPermanentWidget(self.xy)
        self.addPermanentWidget(self.zoom)
        self.addPermanentWidget(self.select)
        self.addWidget(self.msg)
