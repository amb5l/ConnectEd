"""
Main window implementation for the ConnectEd application.

This module provides the main application window, including menu bars,
status bars, and the central MDI area for document management.
"""

__all__ = ['MainWindow']

from PyQt6.QtCore    import Qt, QByteArray
from PyQt6.QtWidgets import QMainWindow, QMdiArea
from PyQt6.QtGui     import QCloseEvent

from ...core         import APP_NAME, connect_actions_to_slots, Design
from .actions        import Actions
from .slots          import Slots
from .menu_bar       import MenuBar
from .status_bar     import StatusBar

from ..messages_view_dock   import MessagesViewDock
from ..transcript_view_dock import TranscriptViewDock
from ..log_view_dock        import LogViewDock

from ..views         import DiagramView, DiagramSubWindow

from ... import hub


class MainWindow(QMainWindow):
    actions           : Actions
    slots             : Slots
    menu_bar          : MenuBar
    status_bar        : StatusBar
    messages_viewer   : MessagesViewDock
    transcript_viewer : TranscriptViewDock
    log_viewer        : LogViewDock
    mdi_area          : QMdiArea

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
        if hasattr(hub.settings, 'startup'):
            if hasattr(hub.settings.startup, 'geometry'):
                if hub.settings.startup.geometry:
                    self.restoreGeometry(QByteArray(hub.settings.startup.geometry))

        # actions and slots
        self.slots = Slots(self)
        self.actions = Actions(self)
        connect_actions_to_slots(self.actions, self.slots)

        # menu bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        # status bar
        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)

        # dock widgets
        self.messages_viewer = MessagesViewDock(self)
        self.addDockWidget(
            Qt.DockWidgetArea.BottomDockWidgetArea,
            self.messages_viewer
        )
        self.transcript_viewer = TranscriptViewDock(self)
        self.addDockWidget(
            Qt.DockWidgetArea.BottomDockWidgetArea,
            self.transcript_viewer
        )
        self.log_viewer = LogViewDock(self)
        self.addDockWidget(
            Qt.DockWidgetArea.BottomDockWidgetArea,
            self.log_viewer
        )
        self.tabifyDockWidget(self.messages_viewer, self.transcript_viewer)
        self.tabifyDockWidget(self.messages_viewer, self.log_viewer)
        self.messages_viewer.raise_()

        # MDI area
        self.mdi_area = QMdiArea()

        # TODO remove this
        test_db = hub.database_manager.new(Design)
        test_diagram = test_db.new_diagram()
        test_view = DiagramView(test_diagram)
        test_sub_window = DiagramSubWindow(self.mdi_area)
        test_sub_window.setWidget(test_view)
        test_sub_window.setWindowTitle("Test Diagram")
        self.mdi_area.addSubWindow(test_sub_window)
        test_sub_window.showMaximized()

        # central widget
        self.setCentralWidget(self.mdi_area)

        # ready message
        self.messages_viewer.text_view.appendPlainText("ConnectEd ready!")

    def closeEvent(self, event : QCloseEvent) -> None:
        hub.settings.startup.geometry = self.saveGeometry().data()
        super().closeEvent(event)
