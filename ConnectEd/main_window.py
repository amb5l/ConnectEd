from PyQt6.QtWidgets import QMainWindow, QMenuBar, QMenu, QMessageBox
from PyQt6.QtGui import QAction
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
        # (attempt to) restore window geometry
        self.settings = QSettings(ORGNAME, APPNAME)
        self.restoreGeometry(self.settings.value("geometry", b""))

        # create a menu bar
        menu_bar = QMenuBar(self)
        # create File menu and add actions
        file_menu = QMenu("File", self)
        new_action = QAction("New", self)
        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        save_as_action = QAction("Save As...", self)
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        # add File menu to the menu bar
        menu_bar.addMenu(file_menu)
        # create Help menu and add actions
        help_menu = QMenu("Help", self)
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        # add Help menu to the menu bar
        menu_bar.addMenu(help_menu)

        # set the menu bar
        self.setMenuBar(menu_bar)

        # create canvas widget
        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)

    def show_about_dialog(self):
        QMessageBox.about(self, "About", "This is a PyQt6 application.")

    def closeEvent(self, event):

        # save window geometry
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)
