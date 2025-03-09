from PyQt6.QtWidgets import QMenuBar, QMenu

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import MainWindow


class MenuBar(QMenuBar):
    def __init__(
        self    : 'MenuBar',
        parent  : 'MainWindow'
    ) -> None:
        super().__init__(parent)
        actions = parent.commands.actions

        self.file_menu = QMenu('&File')
        self.file_menu.addAction(actions.fileExit)

        self.edit_menu = QMenu('&Edit')
        self.edit_menu.addAction(actions.editCancel)

        self.view_menu = QMenu('&View')
        self.view_menu.addAction(actions.viewZoomAll)
        self.view_menu.addAction(actions.viewZoomSheet)
        self.view_menu.addAction(actions.viewZoomWindow)
        self.view_menu.addAction(actions.viewZoomIn)
        self.view_menu.addAction(actions.viewZoomOut)
        self.view_menu.addSeparator()
        self.view_menu.addAction(actions.viewPanUp)
        self.view_menu.addAction(actions.viewPanDown)
        self.view_menu.addAction(actions.viewPanLeft)
        self.view_menu.addAction(actions.viewPanRight)
        self.view_menu.addSeparator()
        self.view_menu.addAction(actions.viewGridDisplay)
        self.view_menu.addAction(actions.viewGridSnap)

        self.place_menu = QMenu('&Place')
        self.place_menu.addAction(actions.placeRectangle)

        self.window_menu = QMenu('&Window')
        self.window_menu.addAction(actions.windowMessages)
        self.window_menu.addAction(actions.windowLog)

        self.help_menu = QMenu('&Help')
        self.help_menu.addAction(actions.helpAbout)

        self.addMenu(self.file_menu)
        self.addMenu(self.edit_menu)
        self.addMenu(self.view_menu)
        self.addMenu(self.place_menu)
        self.addMenu(self.window_menu)
        self.addMenu(self.help_menu)
