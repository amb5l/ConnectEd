from PyQt6.QtWidgets import QMenuBar, QMenu, QMdiSubWindow

from ..private import Action

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .          import MainWindow
    from ...core    import DatabaseManager, Database

class MenuBar(QMenuBar):
    parent : 'MainWindow'

    def __init__(
        self    : 'MenuBar',
        parent  : 'MainWindow'
    ) -> None:
        super().__init__(parent)
        self.parent = parent
        actions = self.parent.actions

        self.file_menu = QMenu('&File')
        self.file_menu.addAction(actions.fileExit)

        self.edit_menu = QMenu('&Edit')
        self.edit_menu.addAction(actions.editCancel)
        self.edit_menu.addAction(actions.editComplete)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(actions.editSlide)
        self.edit_menu.addAction(actions.editMove)

        self.view_menu = QMenu('&View')
        self.view_menu.addAction(actions.viewZoomAll)
        self.view_menu.addAction(actions.viewZoomSheet)
        self.view_menu.addAction(actions.viewZoomWindow)
        self.view_menu.addAction(actions.viewZoomIn)
        self.view_menu.addAction(actions.viewZoomOut)
        self.view_menu.addSeparator()
        self.view_menu.addAction(actions.viewPan)
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
        self.window_menu.addAction(actions.windowTranscript)
        self.window_menu.addAction(actions.windowLog)

        self.help_menu = QMenu('&Help')
        self.help_menu.addAction(actions.helpAbout)

        self.addMenu(self.file_menu)
        self.addMenu(self.edit_menu)
        self.addMenu(self.view_menu)
        self.addMenu(self.place_menu)
        self.addMenu(self.window_menu)
        self.addMenu(self.help_menu)

    def updateWindowMenu(self, dbm : 'DatabaseManager') -> None:
        actions = self.parent.actions
        self.window_menu.clear()
        self.window_menu.addAction(actions.windowMessages)
        self.window_menu.addAction(actions.windowLog)
        if dbm.databases:
            db_subwindows : dict['Database', list[QMdiSubWindow]] = {}
            for subwindow in self.parent.mdi_area.subWindowList():
                if subwindow.widget() is not None:
                    scene = subwindow.widget().scene()
                    if scene is not None:
                        if scene.db is not None:
                            db_subwindows[scene.db].append(subwindow)
            for db in dbm.databases:
                self.window_menu.addSeparator()
                # create a new action for the database navigator
                action = Action(self.parent, db.name, db.path, None, True, False, db_nav)
                action.triggered.connect(self.activateSubWindow)
                self.window_menu.addAction(action)
                # create action(s) for open subwindows
                for subwindow in db_subwindows[db]:
                    action = Action(self.parent, subwindow.windowTitle(), None, None, True)

                # subwindow - view - scene - database

        # update checked status of menu items

    def activateSubWindow(self) -> None:
        sender = self.sender()  # Get the QAction that triggered this slot
        if isinstance(sender, QAction):
            subwindow = sender.data()  # Retrieve the subwindow stored in the action
            if subwindow:
                self.mdi_area.setActiveSubWindow(subwindow)
                subwindow.show()  # Ensure it’s visible
                subwindow.raise_()  # Bring it to the front
                subwindow.setFocus()  # Give it focus