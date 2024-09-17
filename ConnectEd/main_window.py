from PyQt6.QtWidgets import QMainWindow, QMenuBar, QMenu, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSettings

from app import ORG_NAME, APP_NAME, APP_TITLE
from menus import menus
from actions import Actions
from shortcuts import shortcuts
from canvas import Canvas


class MainWindow(QMainWindow):
    def __init__(self, diagram):
        super().__init__()
        self.setWindowTitle(APP_TITLE)

        #-------------------------------------------------------------------------------
        # set up window

        # default size: 50% of screen size
        screen = self.screen()
        screenSize = screen.size()
        width = screenSize.width() // 2
        height = screenSize.height() // 2

        # default position: central
        self.resize(width, height)
        windowRect = self.frameGeometry()
        center = screen.availableGeometry().center()
        self.frameGeometry().moveCenter(center)
        self.move(windowRect.topLeft())

        # (attempt to) restore window geometry from settings
        self.settings = QSettings(ORG_NAME, APP_NAME)
        self.restoreGeometry(self.settings.value("geometry", b""))

        #-------------------------------------------------------------------------------
        # create menus, actions and shortcuts from menus list

        actions = Actions(self)

        def ActionFunction(menuItemActionName):
            return lambda checked=False, name=menuItemActionName: getattr(actions, name)()

        menuBar = QMenuBar(self)
        for menuName, menuItems in menus:
            menu = QMenu(menuName, self)
            for menuItemText, menuItemActionName in menuItems:
                if menuItemText:
                    action = QAction(menuItemText, self)
                    action.triggered.connect(ActionFunction(menuItemActionName))
                    if getattr(shortcuts, menuItemActionName) is not None:
                        action.setShortcut(getattr(shortcuts, menuItemActionName))
                    menu.addAction(action)
                else:
                    menu.addSeparator()
            menuBar.addMenu(menu)
        self.setMenuBar(menuBar)

        #-------------------------------------------------------------------------------
        # create a status bar

        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

        #-------------------------------------------------------------------------------
        # create canvas widget

        self.canvas = Canvas(diagram)
        self.setCentralWidget(self.canvas)

        #-------------------------------------------------------------------------------

    def closeEvent(self, event):
        # save window geometry
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)
