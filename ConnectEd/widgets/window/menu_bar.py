from typing import Self

from PyQt6.QtWidgets import QMenuBar

from ...app import settings

from ..menu import Menu

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Window
    from .actions import Actions


class MenuBar(QMenuBar):
    _menus_dict : dict[str, Menu]

    def __init__(
        self    : Self,
        parent  : "Window"
    ) -> None:
        super().__init__(parent)
        self._menus_dict = {}
        actions = parent.actions

        self.file_menu = Menu("&File")
        self.file_new_menu = Menu("&New")
        self.file_new_menu.addAction(actions.fileNewDesign)
        self.file_new_menu.addAction(actions.fileNewLibrary)
        self.updateFileMenu(actions)

        self.edit_menu = Menu("&Edit")
        self.edit_menu.addAction(actions.editCancel)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(actions.editUndo)
        self.edit_menu.addAction(actions.editRedo)
        # TODO: repeat
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(actions.editCut)
        self.edit_menu.addAction(actions.editCopy)
        self.edit_menu.addAction(actions.editPaste)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(actions.editDelete)
        self.edit_menu.addAction(actions.editDuplicate)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(actions.editSelectArea)
        self.edit_menu.addAction(actions.editSelectAll)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(actions.editProperties)
        self.edit_menu.addAction(actions.editAppearance)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(actions.editQuery)
        # TODO: editFind
        # TODO: editFindNext
        # TODO: editFindPrevious
        # TODO: editFindReplace

        self.view_menu = Menu("&View")
        # TODO: viewNext
        # TODO: viewPrevious
        self.view_menu.addAction(actions.viewZoomAll)
        self.view_menu.addAction(actions.viewZoomSheet)
        self.view_menu.addAction(actions.viewZoomArea)
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
        self.view_menu.addSeparator()
        self.view_theme_menu = Menu("&Theme")
        self.view_theme_menu.addAction(actions.viewThemeDark)
        self.view_theme_menu.addAction(actions.viewThemeLightMono)
        self.view_menu.addMenu(self.view_theme_menu)

        self.place_menu = Menu("&Place")
        self.place_menu.addAction(actions.placePort)
        self.place_menu.addAction(actions.placeBlock)
        self.place_menu.addAction(actions.placeBlockPin)
        self.place_menu.addSeparator()
        self.place_menu.addAction(actions.placeConnection)
        self.place_menu.addSeparator()
        self.place_menu.addAction(actions.placeLine)
        self.place_menu.addAction(actions.placeRectangle)
        self.place_menu.addAction(actions.placeText)
        self.place_menu.addAction(actions.placeTextBlock)

        self.window_menu = Menu("&Window")
        self.window_menu.addAction(actions.windowExplorer)
        self.window_menu.addAction(actions.windowMessages)
        self.window_menu.addAction(actions.windowTranscript)
        self.window_menu.addAction(actions.windowLog)

        self.help_menu = Menu("&Help")
        self.help_menu.addAction(actions.helpAbout)

        self.addMenu(self.file_menu)
        self.addMenu(self.edit_menu)
        self.addMenu(self.view_menu)
        self.addMenu(self.place_menu)
        self.addMenu(self.window_menu)
        self.addMenu(self.help_menu)

        settings().mruChanged.connect(lambda: self.updateFileMenu(actions))

    def addMenu(self : Self, menu : Menu) -> None:
        super().addMenu(menu)
        self._menus_dict[menu.title().replace("&", "")] = menu

    def menusDict(self : Self) -> dict[str, Menu]:
        return self._menus_dict

    def updateWindowMenu(self : Self) -> None:
        window : "Window" = self.parent()
        actions = window.actions
        self.window_menu.clear()
        self.window_menu.addAction(actions.windowExplorer)
        self.window_menu.addAction(actions.windowMessages)
        self.window_menu.addAction(actions.windowTranscript)
        self.window_menu.addAction(actions.windowLog)
        if len(window.mdi_area.subWindowList()) > 1:
            self.window_menu.addSeparator()
            self.window_menu.addAction(actions.windowNext)
            self.window_menu.addAction(actions.windowPrevious)
            subwindow_actions = window.mdi_area.subwindow_actions
            if subwindow_actions == {}:
                return
            for key, actions in subwindow_actions.items():
                if key == "_":
                    continue
                self.window_menu.addSeparator()
                for action in actions:
                    self.window_menu.addAction(action)

    def updateFileMenu(self : Self, actions : "Actions") -> None:
        self.file_menu.clear()
        self.file_menu.addMenu(self.file_new_menu)
        self.file_menu.addAction(actions.fileOpen)
        self.file_menu.addAction(actions.fileSave)
        self.file_menu.addAction(actions.fileSaveAs)
        mru = settings().getMRU()
        if mru:
            self.file_menu.addSeparator()
            for i, file_name in enumerate(mru):
                if file_name == "":
                    break
                action = getattr(actions, f"fileOpenMRU{i + 1}")
                action.setText(f"&{i + 1}: {file_name}")
                self.file_menu.addAction(action)
            self.file_menu.addSeparator()
        self.file_menu.addAction(actions.fileExit)
