from PyQt6.QtWidgets import QMainWindow, QLabel  # Added QLabel for testing

from ...core import APP_NAME
from .commands     import Commands
from .menu_bar     import MenuBar
from .status_bar   import StatusBar
from ...test.dummy_widget import DummyWidget

class MainWindow(QMainWindow):
    def __init__(self : 'MainWindow') -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, 800, 600)
        self.commands = Commands(self)
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)
        self.dummy_widget = DummyWidget()
        self.setCentralWidget(self.dummy_widget)
