"""
Main window implementation for the ConnectEd application.

This module provides the main application window, including menu bars,
status bars, and the central MDI area for document management.
"""

from typing import Self

from PyQt6.QtCore    import Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui     import QIcon, QCloseEvent

from ...app import settings

from ...core.defs  import APP_NAME
from ...core.utils import check

from ...resources import getIconPath

from .actions    import Actions
from .slots      import Slots
from .menu_bar   import MenuBar
from .status_bar import StatusBar
from .mdi_area   import MdiArea

from .text_view       import TextView
from .messages_view   import MessagesViewDock
from .transcript_view import TranscriptViewDock
from .log_view        import LogViewDock
from .explorer        import ExplorerDock, Explorer


class Window(QMainWindow):
    # instance attributes
    actions           : Actions
    slots             : Slots
    _menu_bar         : MenuBar
    status_bar        : StatusBar
    explorer_dock     : ExplorerDock
    messages_viewer   : MessagesViewDock
    transcript_viewer : TranscriptViewDock
    log_viewer        : LogViewDock
    mdi_area          : MdiArea

    # signals
    ready = pyqtSignal()

    def __init__(self : Self) -> None:
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
        self.setWindowIcon(QIcon(getIconPath("ConnectEd.png")))
        self.setUnifiedTitleAndToolBarOnMac(False)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        g = settings().get("startup/geometry")
        if g:
            self.restoreGeometry(g)

        # actions and slots
        self.slots = Slots()
        self.actions = Actions()
        self.connectActionsToSlots(self.actions, self.slots)

        # menu bar
        self._menu_bar = MenuBar(self)
        self.setMenuBar(self._menu_bar)

        # status bar
        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)

        # dock widgets
        qd = Qt.DockWidgetArea
        self.messages_viewer = MessagesViewDock(self)
        self.addDockWidget(qd.BottomDockWidgetArea, self.messages_viewer)
        self.transcript_viewer = TranscriptViewDock(self)
        self.addDockWidget(qd.BottomDockWidgetArea, self.transcript_viewer)
        self.log_viewer = LogViewDock(self)
        self.addDockWidget(qd.BottomDockWidgetArea, self.log_viewer)
        self.tabifyDockWidget(self.messages_viewer, self.transcript_viewer)
        self.tabifyDockWidget(self.messages_viewer, self.log_viewer)
        self.messages_viewer.raise_()
        self.explorer_dock = ExplorerDock(self)
        self.addDockWidget(qd.LeftDockWidgetArea, self.explorer_dock)

        # MDI area
        self.mdi_area = MdiArea()

        # central widget
        self.setCentralWidget(self.mdi_area)

        # signal-slot connections
        self.mdi_area.subWindowActivated.connect(self.actions.onSubWindowActivated)
        self.mdi_area.subWindowActivated.connect(self._menu_bar.updateWindowMenu)
        clipboard = QApplication.clipboard()
        clipboard.dataChanged.connect(self.actions.onClipboardDataChanged)

        # ready
        self.messages_viewer.text_view.appendPlainText("ConnectEd ready!")

    def closeEvent(self : Self, event : QCloseEvent) -> None:
        try:
            self.mdi_area.subWindowActivated.disconnect(
                self.actions.onSubWindowActivated
            )
        except TypeError:
            pass
        try:
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.dataChanged.disconnect(
                    self.actions.onClipboardDataChanged
                )
        except TypeError:
            pass
        if hasattr(self, 'actions') and self.actions:
            self.actions.onSubWindowActivated(None)
        settings().set("startup/geometry", self.saveGeometry().data())
        super().closeEvent(event)

    def connectActionsToSlots(
        self    : Self,
        actions : Actions,
        slots   : Slots
    ) -> None:
        action_names = [a for a in dir(actions) if not a.startswith("_") and not callable(getattr(actions, a))]
        slot_names   = [s for s in dir(slots)   if not s.startswith("_")]
        error = False
        error &= check(len(action_names) > 0, "No actions found")
        error &= check(len(slot_names)   > 0, "No slots found")
        error &= check(len(action_names) == len(slot_names), \
            f"Number of actions ({len(action_names)}) and slots ({len(slot_names)}) do not match")
        for action_name in action_names:
            error &= check(action_name in slot_names, \
                f"No matching slot found for action '{action_name}'")
        for slot_name in slot_names:
            error &= check(slot_name in action_names, \
                f"No matching action found for slot '{slot_name}'")
        if error:
            raise Exception("Action-slot mismatch")
        for action_name in action_names:
            action = getattr(actions, action_name)
            slot = getattr(slots, action_name)
            action.triggered.connect(slot)

    # convenience properties

    @property
    def menu_bar(self : Self) -> MenuBar:
        return self._menu_bar

    @property
    def explorer(self : Self) -> Explorer:
        return self.explorer_dock.widget()

    @property
    def messages(self : Self) -> TextView:
        return self.messages_viewer.text_view

    @property
    def transcript(self : Self) -> TextView:
        return self.transcript_viewer.text_view

    @property
    def log(self : Self) -> TextView:
        return self.log_viewer.text_view
