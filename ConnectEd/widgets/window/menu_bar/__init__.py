from typing import Self

from PyQt6.QtWidgets import QMenuBar

from ....app import settings, window

from ....core.utils import check

from ...menu import Menu, PlaceMenu

from .actions import Actions
from .slots   import Slots

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Window


class MenuBar(QMenuBar):
    _actions    : Actions
    _slots      : Slots
    _menus_dict : dict[str, Menu]

    def __init__(
        self   : Self,
        parent : "Window"
    ) -> None:
        super().__init__(parent)
        self._slots   = Slots()
        self._actions = Actions()
        self._connectActionsToSlots(self._actions, self._slots)

        self._menus_dict = {}
        a = self._actions

        self.file_menu = Menu("&File")
        self.file_new_menu = Menu("&New")
        self.file_new_menu.addAction(a.fileNewDesign)
        self.file_new_menu.addAction(a.fileNewLibrary)
        self.updateFileMenu()

        self.edit_menu = Menu("&Edit")
        self.edit_menu.addAction(a.editCancel)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(a.editUndo)
        self.edit_menu.addAction(a.editRedo)
        # TODO: repeat
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(a.editCut)
        self.edit_menu.addAction(a.editCopy)
        self.edit_menu.addAction(a.editPaste)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(a.editDelete)
        self.edit_menu.addAction(a.editDuplicate)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(a.editSelectArea)
        self.edit_menu.addAction(a.editSelectAll)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(a.editProperties)
        self.edit_menu.addAction(a.editAppearance)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(a.editQuery)
        # TODO: editFind
        # TODO: editFindNext
        # TODO: editFindPrevious
        # TODO: editFindReplace

        self.view_menu = Menu("&View")
        # TODO: viewNext
        # TODO: viewPrevious
        self.view_menu.addAction(a.viewZoomAll)
        self.view_menu.addAction(a.viewZoomSheet)
        self.view_menu.addAction(a.viewZoomArea)
        self.view_menu.addAction(a.viewZoomIn)
        self.view_menu.addAction(a.viewZoomOut)
        self.view_menu.addSeparator()
        self.view_menu.addAction(a.viewPan)
        self.view_menu.addAction(a.viewPanUp)
        self.view_menu.addAction(a.viewPanDown)
        self.view_menu.addAction(a.viewPanLeft)
        self.view_menu.addAction(a.viewPanRight)
        self.view_menu.addSeparator()
        self.view_menu.addAction(a.viewGridDisplay)
        self.view_menu.addAction(a.viewGridSnap)
        self.view_menu.addSeparator()
        self.view_theme_menu = Menu("&Theme")
        self.view_theme_menu.addAction(a.viewThemeDark)
        self.view_theme_menu.addAction(a.viewThemeLightMono)
        self.view_menu.addMenu(self.view_theme_menu)

        self.place_menu = PlaceMenu("&Place")
        self.updatePlaceMenu()

        self.window_menu = Menu("&Window")
        self.updateWindowMenu()

        self.help_menu = Menu("&Help")
        self.help_menu.addAction(a.helpAbout)

        self.addMenu(self.file_menu)
        self.addMenu(self.edit_menu)
        self.addMenu(self.view_menu)
        self.addMenu(self.place_menu)
        self.addMenu(self.window_menu)
        self.addMenu(self.help_menu)

        settings().mruChanged.connect(lambda: self.updateFileMenu())
        window().mdi_area.subWindowActivated.connect(self.updateWindowMenu)
        window().mdi_area.subWindowActivated.connect(self.updatePlaceMenu)


    def addMenu(self : Self, menu : Menu) -> None:
        super().addMenu(menu)
        self._menus_dict[menu.title().replace("&", "")] = menu

    def menusDict(self : Self) -> dict[str, Menu]:
        return self._menus_dict

    def updateFileMenu(self : Self) -> None:
        a = self._actions
        self.file_menu.clear()
        self.file_menu.addMenu(self.file_new_menu)
        self.file_menu.addAction(a.fileOpen)
        self.file_menu.addAction(a.fileSave)
        self.file_menu.addAction(a.fileSaveAs)
        self.file_menu.addAction(a.fileClose)
        mru = settings().getMRU()
        if mru:
            self.file_menu.addSeparator()
            for i, file_name in enumerate(mru):
                if file_name == "":
                    break
                action = getattr(a, f"fileOpenMRU{i + 1}")
                action.setText(f"&{i + 1}: {file_name}")
                self.file_menu.addAction(action)
            self.file_menu.addSeparator()
        self.file_menu.addAction(a.fileExit)

    def updatePlaceMenu(self : Self) -> None:
        from ...graphics.views.diagram import DiagramSubWindow
        from ...graphics.views.symbol  import SymbolSubWindow
        from ..spreadsheet import SpreadsheetSubWindow
        window : "Window" = self.parent()
        a = self._actions
        if not hasattr(window, "mdi_area"):
            return
        subwindow = window.mdi_area.activeSubWindow()
        if subwindow.__class__ == self.place_menu.subwindow_class:
            return  # no change
        self.place_menu.clear()
        if isinstance(window.mdi_area.activeSubWindow(), DiagramSubWindow):
            # Diagram window - show diagram-appropriate actions
            self.place_menu.addAction(a.placePort)
            self.place_menu.addAction(a.placeBlock)
            self.place_menu.addAction(a.placeBlockPin)
            self.place_menu.addSeparator()
            self.place_menu.addAction(a.placeConnection)
            self.place_menu.addSeparator()
            self.place_menu.addAction(a.placeLine)
            self.place_menu.addAction(a.placeRectangle)
            self.place_menu.addAction(a.placeText)
            self.place_menu.addAction(a.placeTextBlock)
            self.place_menu.setEnabled(True)
        elif isinstance(subwindow, SymbolSubWindow):
            # Symbol window - show symbol-appropriate actions
            self.place_menu.addAction(a.placeSymbolPin)
            self.place_menu.addSeparator()
            self.place_menu.addAction(a.placeLine)
            self.place_menu.addAction(a.placeRectangle)
            self.place_menu.addAction(a.placeText)
            self.place_menu.addAction(a.placeTextBlock)
            self.place_menu.setEnabled(True)
        elif isinstance(subwindow, SpreadsheetSubWindow):
            # Spreadsheet window - disable the menu
            self.place_menu.setEnabled(False)
        else:
            # No active window or unknown type - disable the menu
            self.place_menu.setEnabled(False)
        # Remember the current subwindow class
        self.place_menu.subwindow_class = subwindow.__class__

    def updateWindowMenu(self : Self) -> None:
        window : "Window" = self.parent()
        a = self._actions
        self.window_menu.clear()
        self.window_menu.addAction(a.windowNext)
        self.window_menu.addAction(a.windowPrevious)
        self.window_menu.addSeparator()
        self.window_menu.addAction(a.windowNavigator)
        self.window_menu.addAction(a.windowMessages)
        self.window_menu.addAction(a.windowTranscript)
        self.window_menu.addAction(a.windowLog)
        if not hasattr(window, "mdi_area"):
            return
            
        for scene in window.mdi_area.scenesActions().keys():
            self.window_menu.addSeparator()
            for action in window.mdi_area.scenesActions()[scene]:
                self.window_menu.addAction(action)

    def _connectActionsToSlots(
        self    : Self,
        actions : Actions,
        slots   : Slots
    ) -> None:
        action_names = [a for a in dir(actions) \
            if not a.startswith("_") and not callable(getattr(actions, a))]
        slot_names   = [s for s in dir(slots) if not s.startswith("_")]
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
