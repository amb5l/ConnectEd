from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import QSettings

from common import logger, APP_TITLE, ORG_NAME, APP_NAME
from actions.actions import Actions
from menus.menus import MenuBar
from status import StatusBar
from canvas.canvas import Canvas


class MainWindow(QMainWindow):
    def __init__(self, diagram):
        logger.info('MainWindow: initialising')
        super().__init__()
        self.setWindowTitle(APP_TITLE)

        # default size: 50% of screen size, centered
        screen = self.screen()
        screenSize = screen.size()
        self.resize(screenSize / 2)
        windowRect = self.frameGeometry()
        center = self.screen().availableGeometry().center()
        self.frameGeometry().moveCenter(center)
        self.move(windowRect.topLeft())

        # restore window geometry from persistant settings if possible
        settings = QSettings(ORG_NAME, APP_NAME)
        if settings.contains("startup/geometry"):
            self.restoreGeometry(settings.value("geometry", b""))

        actions = Actions(self)
        menuBar = MenuBar(self, actions)
        self.setMenuBar(menuBar)

        self.statusBar = StatusBar(self)
        self.setStatusBar(self.statusBar)

        self.canvas = Canvas(diagram)
        self.setCentralWidget(self.canvas)

    def closeEvent(self, event):
        # save window geometry
        settings = QSettings(ORG_NAME, APP_NAME)
        settings.setValue("startup/geometry", self.saveGeometry())
        super().closeEvent(event)
        self.logger.info('MainWindow: closing')
