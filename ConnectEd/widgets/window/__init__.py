"""
Main window implementation for the ConnectEd application.

This module provides the main application window, including menu bars,
status bars, and the central MDI area for document management.
"""

from typing import Self

from PyQt6.QtCore    import Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui     import QIcon, QCloseEvent

from ...app import app, settings

from ...core.defs  import APP_NAME

from ...resources import getIconPath

from .menu_bar   import MenuBar
from .status_bar import StatusBar
from .mdi_area   import MdiArea

from .text_view       import TextView
from .messages_view   import MessagesViewDock
from .transcript_view import TranscriptViewDock
from .log_view        import LogViewDock
from .navigator       import NavigatorDock, Navigator


class Window(QMainWindow):
    # instance attributes
    _menu_bar         : MenuBar
    status_bar        : StatusBar
    navigator_dock    : NavigatorDock
    messages_viewer   : MessagesViewDock
    transcript_viewer : TranscriptViewDock
    log_viewer        : LogViewDock
    mdi_area          : MdiArea

    # signals
    ready = pyqtSignal()

    def __init__(self : Self) -> None:
        super().__init__()
        app().setWindow(self)
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

        # MDI area
        self.mdi_area = MdiArea()

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
        self.navigator_dock = NavigatorDock(self)
        self.addDockWidget(qd.LeftDockWidgetArea, self.navigator_dock)

        # central widget
        self.setCentralWidget(self.mdi_area)

        # ready
        if not app().cli():
            self.show()
            self.raise_()
            self.activateWindow()
            app().processEvents()
        self.messages_viewer.text_view.appendPlainText("ConnectEd ready!")
        app().ready.window.emit()

    def closeEvent(self : Self, event : QCloseEvent) -> None:
        try:
            self.mdi_area.subWindowActivated.disconnect(
                self.actions.onSubWindowActivated
            )
            self.mdi_area.subWindowActivated.disconnect(
                self._menu_bar.updateWindowMenu
            )
            self.mdi_area.subWindowActivated.disconnect(
                self._menu_bar.updatePlaceMenu
            )
        except TypeError: # workaround for Qt cleanup
            pass
        try:
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.dataChanged.disconnect(
                    self.actions.onClipboardDataChanged
                )
        except TypeError: # workaround for Qt cleanup
            pass
        if hasattr(self, 'actions') and self.actions:
            self.actions.onSubWindowActivated(None)
        settings().set("startup/geometry", self.saveGeometry().data())
        super().closeEvent(event)

    # convenience properties

    @property
    def menu_bar(self : Self) -> MenuBar:
        return self._menu_bar

    @property
    def navigator(self : Self) -> Navigator:
        return self.navigator_dock.widget()

    @property
    def messages(self : Self) -> TextView:
        return self.messages_viewer.text_view

    @property
    def transcript(self : Self) -> TextView:
        return self.transcript_viewer.text_view

    @property
    def log(self : Self) -> TextView:
        return self.log_viewer.text_view
