"""
Main window implementation for the ConnectEd application.

This module provides the main application window, including menu bars,
status bars, and the central MDI area for document management.
"""

__all__ = [
    'MainWindow'
]

from PyQt6.QtCore    import Qt, QByteArray
from PyQt6.QtWidgets import QMainWindow, QMdiArea, QMdiSubWindow

from ...core         import APP_NAME, logger, settings
from .commands       import Commands
from .menu_bar       import MenuBar
from .status_bar     import StatusBar
from ..msg_view_dock import MsgViewDock
from ..log_view_dock import LogViewDock

from ...test.dummy_widget import DummyWidget

from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from ..drawing import Drawing, DrawingSubWindow


class MainWindow(QMainWindow):
    """Main window implementation for the ConnectEd application."""

    commands   : Commands
    menu_bar   : MenuBar
    status_bar : StatusBar
    msg_viewer : MsgViewDock
    log_viewer : LogViewDock
    mdi_area   : QMdiArea


    def __init__(self : 'MainWindow') -> None:
        super().__init__()

        # default position
        screen = self.screen()
        screenSize = screen.size()
        self.resize(screenSize.width() // 2, screenSize.height() // 2)
        frame_geometry = self.frameGeometry()
        centerPoint = screen.availableGeometry().center()
        frame_geometry.moveCenter(centerPoint)
        self.move(frame_geometry.topLeft())

        # saved position
        self.setWindowTitle(APP_NAME)
        if hasattr(settings, 'startup'):
            if hasattr(settings.startup, 'geometry'):
                if settings.startup.geometry:
                    self.restoreGeometry(QByteArray(settings.startup.geometry))

        # commands = actions and slots
        self.commands = Commands(self)

        # menu bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        # status bar
        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)

        # dock widgets
        self.msg_viewer = MsgViewDock(self)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.msg_viewer)
        self.log_viewer = LogViewDock(self)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.log_viewer)
        self.tabifyDockWidget(self.msg_viewer, self.log_viewer)
        self.msg_viewer.raise_()

        # MDI area
        self.mdi_area = QMdiArea()

        # TODO remove this
        # Import here to avoid circular dependency
        from ..diagram import Diagram, DiagramSubWindow
        test_sub_window = DiagramSubWindow(self.mdi_area)
        test_widget = Diagram(test_sub_window, self)
        test_sub_window.setWidget(test_widget)
        test_sub_window.setWindowTitle("Test Diagram")
        self.mdi_area.addSubWindow(test_sub_window)
        test_sub_window.showMaximized()

        # central widget
        self.setCentralWidget(self.mdi_area)

        # ready message
        self.msg_viewer.text_view.appendPlainText("ConnectEd ready!")

    def closeEvent(self, event):
        settings.startup.geometry = self.saveGeometry().data()
        super().closeEvent(event)
