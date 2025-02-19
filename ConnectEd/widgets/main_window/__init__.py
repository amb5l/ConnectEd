from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QMainWindow, QDockWidget

from ...core            import APP_NAME, LOG_FILENAME
from .commands          import Commands
from .menu_bar          import MenuBar
from .status_bar        import StatusBar
from ..text_file_viewer import TextFileViewer
from ...core.logger     import add_log_viewer_handler

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
        self.log_viewer = TextFileViewer(self, LOG_FILENAME)
        self.log_viewer_dock_widget = QDockWidget('Log Viewer')
        self.log_viewer_dock_widget.setWidget(self.log_viewer)
        add_log_viewer_handler(self.log_viewer)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.log_viewer_dock_widget)
