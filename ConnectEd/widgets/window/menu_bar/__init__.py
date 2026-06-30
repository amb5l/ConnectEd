from __future__ import annotations

from typing import Self

from PyQt6.QtWidgets import QMenuBar

from ....app import settings, window

from ....core.check import checked

from ...menu import Menu, PlaceMenu

from ....ai.profiles import loadProfiles, profileMenuLabel

from ...action import Action

from ...graphics.views.diagram import DiagramSubWindow

from .actions import Actions
from .slots   import Slots

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...graphics.views.diagram import DiagramView
    from .. import Window


class MenuBar(QMenuBar):
    _actions : Actions
    _slots   : Slots
    _menus   : dict[str, Menu]

    @checked
    def __init__(
        self   : Self,
        parent : Window
    ) -> None:
        super().__init__(parent)
        self._slots   = Slots()
        self._actions = Actions(self._slots)

        self._menus = {}
        a = self._actions

        self.file_menu = Menu("&File")
        self.updateFileMenu()
        settings().mruChanged.connect(self.updateFileMenu)

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
        self.updateViewMenu()

        self.place_menu = PlaceMenu("&Place")
        self.updatePlaceMenu()

        self.ai_menu = Menu("&AI")
        self.ai_new_chat_menu = Menu("&New Chat")
        self.updateAiMenu()

        self.window_menu = Menu("&Window")
        self.updateWindowMenu()

        self.help_menu = Menu("&Help")
        self.help_menu.addAction(a.helpAbout)

        self.addMenu(self.file_menu)
        self.addMenu(self.edit_menu)
        self.addMenu(self.view_menu)
        self.addMenu(self.place_menu)
        self.addMenu(self.ai_menu)
        self.addMenu(self.window_menu)
        self.addMenu(self.help_menu)

        # non-menu actions
        window().addAction(a.editRotateCW)
        window().addAction(a.editRotateCCW)

        settings().mruChanged.connect(lambda: self.updateFileMenu())
        window().mdiArea().subWindowActivated.connect(self.updateWindowMenu)
        window().mdiArea().subWindowActivated.connect(self.updatePlaceMenu)

    def addMenu(self : Self, menu : Menu) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        super().addMenu(menu)
        self._menus[menu.title().replace("&", "")] = menu

    def getMenus(self : Self) -> dict[str, Menu]:
        return self._menus

    def updateFileMenu(self : Self) -> None:
        a = self._actions
        self.file_menu.clear()
        self.file_menu.addAction(a.fileNew)
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

    def updateViewMenu(self : Self) -> None:
        en = False
        en_zoom_in = False
        en_zoom_out = False
        subwindow = window().mdiArea().activeSubWindow()
        if subwindow is not None:
            widget = subwindow.widget()
            if isinstance(widget, DiagramView):
                en = True
                zoom = widget.zoom
                en_zoom_in = zoom < settings().get("display/zoom/max")
                en_zoom_out = zoom > settings().get("display/zoom/min")
        a = self._actions
        a.viewZoomAll.setEnabled(en)
        a.viewZoomSheet.setEnabled(en and isinstance(subwindow, DiagramSubWindow))
        a.viewZoomArea.setEnabled(en)
        a.viewZoomIn.setEnabled(en and en_zoom_in)
        a.viewZoomOut.setEnabled(en and en_zoom_out)
        a.viewPan.setEnabled(en)
        a.viewPanUp.setEnabled(en)
        a.viewPanDown.setEnabled(en)
        a.viewPanLeft.setEnabled(en)
        a.viewPanRight.setEnabled(en)
        a.viewGridDisplay.setEnabled(en)
        a.viewGridSnap.setEnabled(en)

    def updatePlaceMenu(self : Self) -> None:
        from ...graphics.views.diagram import DiagramSubWindow
        from ...graphics.views.symbol  import SymbolSubWindow
        from ..spreadsheet import SpreadsheetSubWindow
        subwindow = window().mdiArea().activeSubWindow()
        if subwindow.__class__ == self.place_menu.subwindow_cls:
            return  # no change
        self.place_menu.clear()
        a = self._actions
        if isinstance(subwindow, DiagramSubWindow):
            # Diagram window - show diagram-appropriate actions
            self.place_menu.addAction(a.placePort)
            self.place_menu.addAction(a.placeGate)
            self.place_menu.addAction(a.placeBlock)
            self.place_menu.addAction(a.placeBlockPin)
            self.place_menu.addSeparator()
            self.place_menu.addAction(a.placeConnection)
            self.place_menu.addAction(a.placeTap)
            self.place_menu.addAction(a.placeNetLabel)
            self.place_menu.addSeparator()
            self.place_menu.addAction(a.placeLine)
            self.place_menu.addAction(a.placeRectangle)
            self.place_menu.addAction(a.placeEllipse)
            self.place_menu.addAction(a.placePolyline)
            self.place_menu.addAction(a.placeText)
            self.place_menu.setEnabled(True)
        elif isinstance(subwindow, SymbolSubWindow):
            # Symbol window - show symbol-appropriate actions
            self.place_menu.addAction(a.placeSymbolPin)
            self.place_menu.addSeparator()
            self.place_menu.addAction(a.placeLine)
            self.place_menu.addAction(a.placeRectangle)
            self.place_menu.addAction(a.placeEllipse)
            self.place_menu.addAction(a.placePolyline)
            self.place_menu.addAction(a.placeText)
            self.place_menu.setEnabled(True)
        elif isinstance(subwindow, SpreadsheetSubWindow):
            # Spreadsheet window - disable the menu
            self.place_menu.setEnabled(False)
        else:
            # No active window or unknown type - disable the menu
            self.place_menu.setEnabled(False)
        # Remember the current subwindow class
        self.place_menu.subwindow_cls = subwindow.__class__

    def updateAiMenu(self : Self) -> None:
        a = self._actions
        self.ai_menu.clear()
        self.ai_new_chat_menu.clear()
        manager = window().aiChatManager()
        profiles = loadProfiles()
        if profiles:
            for profile in profiles:
                label = profileMenuLabel(profile)
                models_menu = Menu(label)
                models = profile.cached_models
                if models:
                    for model in models:
                        action = Action(
                            window(),
                            model,
                            f"New chat using {label} with {model}",
                            data = (profile.id, model),
                        )
                        if manager is not None:
                            action.triggered.connect(
                                lambda checked=False,
                                pid=profile.id,
                                m=model : manager.newChat(
                                    profile_id = pid,
                                    model      = m,
                                )
                            )
                        models_menu.addAction(action)
                else:
                    action = Action(
                        window(),
                        "(no models)",
                        f"No models cached for {label}",
                    )
                    action.setEnabled(False)
                    models_menu.addAction(action)
                self.ai_new_chat_menu.addMenu(models_menu)
        else:
            action = Action(
                window(),
                "(add an AI profile)",
                "Add an AI profile in AI → Settings…",
            )
            action.setEnabled(False)
            self.ai_new_chat_menu.addAction(action)
        self.ai_menu.addMenu(self.ai_new_chat_menu)
        if manager is not None:
            chats = manager.chats()
            if chats:
                self.ai_menu.addSeparator()
                for dock in chats:
                    title = dock.windowTitle()
                    action = Action(
                        window(),
                        title,
                        f"Show {title}",
                    )
                    action.triggered.connect(
                        lambda checked=False, d=dock : manager.focusChat(d)
                    )
                    self.ai_menu.addAction(action)
        self.ai_menu.addSeparator()
        self.ai_menu.addAction(a.aiSettings)

    def updateWindowMenu(self : Self) -> None:
        a = self._actions
        self.window_menu.clear()
        self.window_menu.addAction(a.windowNext)
        self.window_menu.addAction(a.windowPrevious)
        self.window_menu.addSeparator()
        self.window_menu.addAction(a.windowNavigator)
        self.window_menu.addAction(a.windowMessages)
        self.window_menu.addAction(a.windowTranscript)
        self.window_menu.addAction(a.windowLog)
        for subjects in window().mdiArea().subWindowActions().values():
            self.window_menu.addSeparator()
            for actions in subjects.values():
                for action in actions:
                    self.window_menu.addAction(action)
