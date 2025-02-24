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

        self.window_menu = QMenu('&Window')
        self.window_menu.addAction(actions.windowMessages)
        self.window_menu.addAction(actions.windowLog)

        self.help_menu = QMenu('&Help')
        self.help_menu.addAction(actions.helpAbout)

        self.addMenu(self.file_menu)
        self.addMenu(self.window_menu)
        self.addMenu(self.help_menu)
