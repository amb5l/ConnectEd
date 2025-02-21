from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QMainWindow, QDockWidget

from ...core        import APP_NAME, LOG_FILENAME
from .commands      import Commands
from .menu_bar      import MenuBar
from .status_bar    import StatusBar
from ..dock_widgets import MsgViewer, LogViewer

from ...test.dummy_widget import DummyWidget

class MainWindow(QMainWindow):
    def __init__(self : 'MainWindow') -> None:
        super().__init__()

        # title and position
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, 800, 600)

        # commands = actions and slots
        self.commands = Commands(self)

        # menu bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        # status bar
        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)

        # dock widgets
        self.msg_viewer = MsgViewer(self)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.msg_viewer)
        self.log_viewer = LogViewer(self)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.log_viewer)
        self.tabifyDockWidget(self.msg_viewer, self.log_viewer)
        self.msg_viewer.raise_()

        # central widget
        self.dummy_widget = DummyWidget()
        self.setCentralWidget(self.dummy_widget)

        self.msg_viewer.text_viewer.appendPlainText("ConnectEd ready!")
