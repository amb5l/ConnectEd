from typing import Self

from PyQt6.QtWidgets import QMenuBar, QMenu

from ... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import MainWindow

class MenuBar(QMenuBar):
    def __init__(
        self    : Self,
        parent  : "MainWindow"
    ) -> None:
        super().__init__(parent)
        actions = parent.actions

        self.file_menu = QMenu("&File")
        self.file_new_menu = QMenu("&New")
        self.file_new_menu.addAction(actions.fileNewDesign)
        self.file_new_menu.addAction(actions.fileNewLibrary)
        self.file_menu.addMenu(self.file_new_menu)
        self.file_menu.addAction(actions.fileOpen)
        self.file_menu.addAction(actions.fileSave)
        self.file_menu.addAction(actions.fileSaveAs)
        self.file_menu.addAction(actions.fileExit)

        self.edit_menu = QMenu("&Edit")
        self.edit_menu.addAction(actions.editUndo)
        self.edit_menu.addAction(actions.editRedo)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(actions.editCancel)
        self.edit_menu.addAction(actions.editComplete)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(actions.editCut)
        self.edit_menu.addAction(actions.editCopy)
        self.edit_menu.addAction(actions.editPaste)
        self.edit_menu.addAction(actions.editDelete)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(actions.editSlide)
        self.edit_menu.addAction(actions.editMove)
        self.edit_menu.addAction(actions.editResize)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(actions.editAppearance)
        # TODO: editFind
        # TODO: editFindNext
        # TODO: editFindPrevious
        # TODO: editFindReplace

        self.view_menu = QMenu("&View")
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

        self.place_menu = QMenu("&Place")
        self.place_menu.addAction(actions.placeRectangle)
        self.place_menu.addAction(actions.placeTextBlock)

        self.window_menu = QMenu("&Window")
        self.window_menu.addAction(actions.windowExplorer)
        self.window_menu.addAction(actions.windowMessages)
        self.window_menu.addAction(actions.windowTranscript)
        self.window_menu.addAction(actions.windowLog)

        self.help_menu = QMenu("&Help")
        self.help_menu.addAction(actions.helpAbout)

        self.addMenu(self.file_menu)
        self.addMenu(self.edit_menu)
        self.addMenu(self.view_menu)
        self.addMenu(self.place_menu)
        self.addMenu(self.window_menu)
        self.addMenu(self.help_menu)

    def updateWindowMenu(self : Self) -> None:
        actions = hub.main_window.actions
        self.window_menu.clear()
        self.window_menu.addAction(actions.windowExplorer)
        self.window_menu.addAction(actions.windowMessages)
        self.window_menu.addAction(actions.windowTranscript)
        self.window_menu.addAction(actions.windowLog)
        if len(hub.main_window.mdi_area.subWindowList()) > 1:
            self.window_menu.addSeparator()
            self.window_menu.addAction(actions.windowNext)
            self.window_menu.addAction(actions.windowPrevious)
            subwindow_actions = hub.main_window.mdi_area.subwindow_actions
            if subwindow_actions == {}:
                return
            for key, actions in subwindow_actions.items():
                if key == "_":
                    continue
                self.window_menu.addSeparator()
                for action in actions:
                    self.window_menu.addAction(action)
