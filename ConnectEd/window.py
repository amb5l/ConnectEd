from PyQt6.QtWidgets import QMainWindow, QMessageBox

from common   import logger, APP_NAME
from settings import startup
from commands import Commands
from menus    import MenuBar
from status   import StatusBar
from canvas   import Canvas


class MainWindow(QMainWindow):
    def __init__(self, diagram):
        logger.info('entry')
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.diagram = diagram
        diagram.setWindow(self)

        if 'geometry' in startup:
            self.restoreGeometry(startup['geometry'])
        else:
            # default size: 50% of screen size, centered
            screen = self.screen()
            screenSize = screen.size()
            self.resize(screenSize / 2)
            windowRect = self.frameGeometry()
            center = self.screen().availableGeometry().center()
            self.frameGeometry().moveCenter(center)
            self.move(windowRect.topLeft())

        self.canvas = Canvas(self, diagram)
        self.setCentralWidget(self.canvas)
        self.commands = Commands(diagram)
        self.commands.update()
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.statusbar = StatusBar(self)
        self.setStatusBar(self.statusbar)

    def closeEvent(self, event):
        # save window geometry
        startup['geometry'] = self.saveGeometry()
        super().closeEvent(event)
        logger.info('MainWindow: closing')

    def todo(self):
        QMessageBox.about(self, "TODO", stack()[1].function)

# The MainWindow presents menus (and may present toolbars).
# These include actions that are connected to slots (functions).
# These actions and functions are contained by MainWindow.
# Most functions are forwarded to the appropriate diagram, via the canvas that
# contains it. Some are handled by the canvas itself.
# This structure is necessary to support multiple canvases/diagrams.

# During initialisation of MainWindow, the central command definitions are checked
# to ensure all actions and slots are...
