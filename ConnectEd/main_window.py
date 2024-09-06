from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import QSettings

from constants import ORGNAME, APPNAME, APPTITLE
from canvas import Canvas

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APPTITLE)
        # set default window size to 50% of screen size
        screen = self.screen()
        screen_size = screen.size()
        width = screen_size.width() // 2
        height = screen_size.height() // 2
        self.resize(width, height)
        # set default window position to centre of screen
        window_rect = self.frameGeometry()
        center_point = screen.availableGeometry().center()
        window_rect.moveCenter(center_point)
        self.move(window_rect.topLeft())
        # create canvas widget
        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)
        # (attempt to) restore window geometry
        self.settings = QSettings(ORGNAME, APPNAME)
        self.restoreGeometry(self.settings.value("geometry", b""))

    def closeEvent(self, event):
        # save window geometry
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)
