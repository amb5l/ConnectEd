# actions and slots are contained in Commands instance

from PyQt6.QtWidgets import QMainWindow, QMdiArea

from common      import logger
from settings    import APP_NAME, startup
from canvas      import Canvas
from .ui.status   import StatusBar
from .ui.menus    import MenuBar
from .ui.slots    import Slots
from .ui.commands import Commands
from .events      import MainWindowEventsMixin
from .api.file    import MainWindowApiFileMixin
from .api.help    import MainWindowApiHelpMixin

class MainWindow(
    QMainWindow,
    MainWindowEventsMixin,
    MainWindowApiFileMixin,
    MainWindowApiHelpMixin
):
    def __init__(self):
        logger.info('entry')
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.diagrams = []
        self.sub_windows = []
        # geometry
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
        # status bar
        self.statusbar = StatusBar(self)
        self.setStatusBar(self.statusbar)
        # MDI area
        self.mdi_area = QMdiArea(self)
        self.setCentralWidget(self.mdi_area)
        # Commands (actions and slots)
        self.commands = Commands(self)
        self.commands.update()
        # Menu bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)



    def addDiagram(self, diagram):
        canvas = Canvas(diagram)
        sub_window = super().addSubWindow(canvas)
        self.sub_windows.append(sub_window)

        sub_window.showMaximized()
