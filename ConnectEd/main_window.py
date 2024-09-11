from PyQt6.QtWidgets import QMainWindow, QMenuBar, QMenu, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSettings

from app import ORG_NAME, APP_NAME, APP_TITLE
from menus import menus
from actions import actions
from shortcuts import shortcuts
from canvas import Canvas


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)

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
        # (attempt to) restore window geometry
        self.settings = QSettings(ORG_NAME, APP_NAME)
        self.restoreGeometry(self.settings.value("geometry", b""))

        #-------------------------------------------------------------------------------
        # menus

        def ActionFunction(menuItemActionName):
            return lambda checked=False, name=menuItemActionName: getattr(actions, name)(self)

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
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # create canvas widget
        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)

    def bounce(self):
        actions.helpAbout(self)

    def show_about_dialog(self):
        """Method does blah"""
        QMessageBox.about(self, "About", "This is a PyQt6 application.")

    def closeEvent(self, event):
        # save window geometry
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)
