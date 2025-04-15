"""
Main window implementation for the ConnectEd application.

This module provides the main application window, including menu bars,
status bars, and the central MDI area for document management.
"""

__all__ = ['MainWindow']

from PyQt6.QtCore    import Qt, QByteArray
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui     import QCloseEvent

from ...core         import APP_NAME, check
from .actions        import Actions
from .slots          import Slots
from .menu_bar       import MenuBar
from .status_bar     import StatusBar
from .mdi_area       import MdiArea

from ..messages_view_dock   import MessagesViewDock
from ..transcript_view_dock import TranscriptViewDock
from ..log_view_dock        import LogViewDock
from ..explorer_dock        import ExplorerDock

from ... import hub


class MainWindow(QMainWindow):
    actions           : Actions
    slots             : Slots
    menu_bar          : MenuBar
    status_bar        : StatusBar
    messages_viewer   : MessagesViewDock
    transcript_viewer : TranscriptViewDock
    log_viewer        : LogViewDock
    mdi_area          : MdiArea

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
                g = hub.settings.startup.geometry
                if g:
                    self.restoreGeometry(bytes.fromhex(g))

        # actions and slots
        self.slots = Slots(self)
        self.actions = Actions(self)
        self.connectActionsToSlots(self.actions, self.slots)

        # menu bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        # status bar
        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)

        # text viewer dock widgets
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

        # DB explorer dock widget
        self.explorer = ExplorerDock(self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.explorer)

        # MDI area
        self.mdi_area = MdiArea()

        # central widget
        self.setCentralWidget(self.mdi_area)

        # ready message
        self.messages_viewer.text_view.appendPlainText("ConnectEd ready!")

    def closeEvent(self : 'MainWindow', event : QCloseEvent) -> None:
        hub.settings.startup.geometry = self.saveGeometry().data()
        super().closeEvent(event)

    def connectActionsToSlots(
        self    : 'MainWindow',
        actions : Actions,
        slots   : Slots
    ) -> None:
        action_names = [a for a in dir(actions) if not a.startswith('_') and not callable(getattr(actions, a))]
        slot_names   = [s for s in dir(slots)   if not s.startswith('_')]
        error = False
        error &= check(len(action_names) > 0, 'No actions found')
        error &= check(len(slot_names)   > 0, 'No slots found')
        error &= check(len(action_names) == len(slot_names), \
            f'Number of actions ({len(action_names)}) and slots ({len(slot_names)}) do not match')
        for action_name in action_names:
            error &= check(action_name in slot_names, \
                f'No matching slot found for action "{action_name}"')
        for slot_name in slot_names:
            error &= check(slot_name in action_names, \
                f'No matching action found for slot "{slot_name}"')
        if error:
            raise Exception('Action-slot mismatch')
        for action_name in action_names:
            action = getattr(actions, action_name)
            slot = getattr(slots, action_name)
            action.triggered.connect(slot)
