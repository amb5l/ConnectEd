"""
Main window implementation for the ConnectEd application.

This module provides the main application window, including menu bars,
status bars, and the central MDI area for document management.
"""

from typing import Self

from PyQt6.QtCore    import Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QMdiSubWindow
from PyQt6.QtGui     import QIcon, QCloseEvent

from ...app import app, logger, settings

from ...core.check import checked
from ...core.defs  import APP_NAME

from ...resources import getIconPath

from ...ai.lock import AiEditLock

from ..graphics.views.diagram import DiagramView

from .menu_bar   import MenuBar
from .status_bar import StatusBar
from .mdi_area   import MdiArea

from .navigator       import NavigatorDock, Navigator
from .netlist         import NetlistBrowserDock, NetlistBrowser
from .text_view       import TextView
from .messages_view   import MessagesViewDock
from .transcript_view import TranscriptViewDock
from .log_view        import LogViewDock
from .ai              import AiChatDock, AiChatManager, AiManager


class Window(QMainWindow):
    # instance attributes
    _menu_bar        : MenuBar
    _status_bar      : StatusBar
    _navigator_dock  : NavigatorDock
    _netlist_dock    : NetlistBrowserDock
    _messages_dock   : MessagesViewDock
    _transcript_dock : TranscriptViewDock
    _log_dock        : LogViewDock
    _ai_manager      : AiManager
    _mdi_area        : MdiArea

    # signals
    ready = pyqtSignal()

    @checked
    def __init__(self : Self) -> None:
        super().__init__()
        app().setWindow(self)
        # default position
        if (screen := self.screen()) is None:
            raise RuntimeError("No screen")
        screen_size = screen.size()
        self.resize(screen_size.width() // 2, screen_size.height() // 2)
        frame_geometry = self.frameGeometry()
        center_point = screen.availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

        # saved position
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(getIconPath("ConnectEd.png")))
        self.setUnifiedTitleAndToolBarOnMac(False)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        g = settings().get("startup/geometry")
        if g:
            self.restoreGeometry(g)

        # MDI area
        self._mdi_area = MdiArea()
        self._mdi_area.subWindowActivated.connect(self._onSubWindowActivated)

        # menu bar
        self._menu_bar = MenuBar(self)
        self.setMenuBar(self._menu_bar)

        # status bar
        self._status_bar = StatusBar(self)
        self.setStatusBar(self._status_bar)

        # dock widgets — bottom: Messages/Transcript/Log (left tabs) | AI Chat (right)
        qd = Qt.DockWidgetArea
        self._messages_dock = MessagesViewDock(self)
        self.addDockWidget(qd.BottomDockWidgetArea, self._messages_dock)
        self._ai_manager = AiManager(self, self._messages_dock)
        self._ai_manager.chatManager().newChat()
        self._transcript_dock = TranscriptViewDock(self)
        self.addDockWidget(qd.BottomDockWidgetArea, self._transcript_dock)
        self._log_dock = LogViewDock(self)
        self.addDockWidget(qd.BottomDockWidgetArea, self._log_dock)
        self.tabifyDockWidget(self._messages_dock, self._transcript_dock)
        self.tabifyDockWidget(self._messages_dock, self._log_dock)
        self._messages_dock.raise_()
        self._menu_bar.updateAiMenu()
        self._ai_manager.scheduleStartup()
        self._navigator_dock = NavigatorDock(self)
        self.addDockWidget(qd.LeftDockWidgetArea, self._navigator_dock)
        self._netlist_dock = NetlistBrowserDock(self)
        self.addDockWidget(qd.LeftDockWidgetArea, self._netlist_dock)
        self.splitDockWidget(
            self._navigator_dock,
            self._netlist_dock,
            Qt.Orientation.Vertical,
        )

        # central widget
        self.setCentralWidget(self._mdi_area)

        # ready
        if not app().cli():
            self.show()
            self.raise_()
            self.activateWindow()
            app().processEvents()
        messages = self.messages()
        if messages:
            messages.appendPlainText("ConnectEd ready!")
        app().ready.window.emit()

    def closeEvent(self : Self, a0 : QCloseEvent | None) -> None:
        if a0 is None:
            logger().warning("No close event")
            return
        try:
            self._mdi_area.subWindowActivated.disconnect(
                self._menu_bar._actions.onSubWindowActivated
            )
            self._mdi_area.subWindowActivated.disconnect(
                self._menu_bar.updateWindowMenu
            )
            self._mdi_area.subWindowActivated.disconnect(
                self._menu_bar.updatePlaceMenu
            )
            self._mdi_area.subWindowActivated.disconnect(
                self._onSubWindowActivated
            )
        except TypeError: # workaround for Qt cleanup
            pass
        try:
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.dataChanged.disconnect(
                    self._menu_bar._actions.onClipboardDataChanged
                )
        except TypeError: # workaround for Qt cleanup
            pass
        settings().set("startup/geometry", self.saveGeometry().data())
        super().closeEvent(a0)

    def _onSubWindowActivated(
        self      : Self,
        subwindow : QMdiSubWindow | None
    ) -> None:
        view = subwindow.widget() if subwindow else None
        diagram = view.scene() if isinstance(view, DiagramView) else None
        netlist = self.netlist()
        if netlist:
            netlist.setDiagram(diagram)

    # convenience methods

    @checked
    def menuBar(self : Self) -> MenuBar | None:
        if not hasattr(self, "_menu_bar"):
            return None
        return self._menu_bar

    @checked
    def statusBar(self : Self) -> StatusBar:
        return self._status_bar

    @checked
    def navigatorDock(self : Self) -> NavigatorDock | None:
        if not hasattr(self, "_navigator_dock"):
            return None
        return self._navigator_dock

    @checked
    def navigator(self : Self) -> Navigator:
        if (dock := self.navigatorDock()) is None:
            raise RuntimeError("Navigator dock not initialized")
        if (widget := dock.widget()) is None:
            raise RuntimeError("Navigator widget not initialized")
        if not isinstance(widget, Navigator):
            raise RuntimeError("Navigator widget is not a Navigator")
        return widget

    @checked
    def netlistDock(self : Self) -> NetlistBrowserDock | None:
        if not hasattr(self, "_netlist_dock"):
            return None
        return self._netlist_dock

    @checked
    def netlist(self : Self) -> NetlistBrowser | None:
        if (dock := self.netlistDock()) is None:
            return None
        widget = dock.widget()
        return widget if isinstance(widget, NetlistBrowser) else None

    @checked
    def messagesDock(self : Self) -> MessagesViewDock | None:
        if not hasattr(self, "_messages_dock"):
            return None
        return self._messages_dock

    @checked
    def messages(self : Self) -> TextView | None:
        if (dock := self.messagesDock()) is None:
            return None
        return dock._text_view

    @checked
    def transcriptDock(self : Self) -> TranscriptViewDock | None:
        if not hasattr(self, "_transcript_dock"):
            return None
        return self._transcript_dock

    @checked
    def transcript(self : Self) -> TextView | None:
        if (dock := self.transcriptDock()) is None:
            return None
        return dock._text_view

    @checked
    def logDock(self : Self) -> LogViewDock | None:
        if not hasattr(self, "_log_dock"):
            return None
        return self._log_dock

    @checked
    def log(self : Self) -> TextView | None:
        if (dock := self.logDock()) is None:
            return None
        return dock._text_view

    @checked
    def aiManager(self : Self) -> AiManager | None:
        if not hasattr(self, "_ai_manager"):
            return None
        return self._ai_manager

    @checked
    def aiEditLock(self : Self) -> AiEditLock | None:
        if (manager := self.aiManager()) is None:
            return None
        return manager.editLock()

    @checked
    def aiChatManager(self : Self) -> AiChatManager | None:
        if (manager := self.aiManager()) is None:
            return None
        return manager.chatManager()

    @checked
    def aiChatDock(self : Self) -> AiChatDock | None:
        if (manager := self.aiChatManager()) is None:
            return None
        chats = manager.chats()
        if not chats:
            return None
        return chats[0]

    @checked
    def mdiArea(self : Self) -> MdiArea:
        if not hasattr(self, "_mdi_area"):
            raise RuntimeError("Window MDI area not initialized")
        return self._mdi_area
