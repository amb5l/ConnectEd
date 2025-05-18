import re

from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QMdiArea, QWidget, QMdiSubWindow

from ..private import Action
from .. import DrawingSubWindow, DrawingView, Drawing

from ... import hub


class MdiArea(QMdiArea):
    subwindow_actions : dict[any, list[Action]]
    subwindow_scenes  : dict[any, list[QMdiSubWindow]]

    def addSubWindow(
        self   : Self,
        widget : QWidget,
        flags  : Qt.WindowType = Qt.WindowType.SubWindow
    ) -> None:
        super().addSubWindow(widget, flags)
        if not isinstance(widget, DrawingSubWindow):
            return
        if not isinstance(widget.widget(), DrawingView):
            return
        if not isinstance(widget.widget().scene(), Drawing):
            return
        self.update()

    def nextSubWindow(self : Self) -> None:
        self._activateSubWindowIndexOffset(1)

    def previousSubWindow(self : Self) -> None:
        self._activateSubWindowIndexOffset(-1)

    def update(self : Self) -> None:
        self._updateSubWindowTitles()
        self._updateSubWindowActions()
        hub.main_window.menu_bar.updateWindowMenu()

    def _updateSubWindowTitles(self : Self) -> None:
        self.subwindow_scenes = {}
        for w in self.subWindowList():
            key = "_"
            if isinstance(w, DrawingSubWindow) \
            and isinstance(w.widget(), DrawingView) \
            and isinstance(w.widget().scene(), Drawing):
                scene = w.widget().scene()
                scene_name = scene.name
                db_name = hub.model.getDbItemFromScene(scene).text()
                w.setWindowTitle(f"{db_name}:{scene_name}")
                key = id(scene)
                if key in self.subwindow_scenes:
                    l = self.subwindow_scenes[key]
                    if len(l) == 1:
                        l[0].setWindowTitle(f"{l[0].windowTitle()}:0")
                    w.setWindowTitle(f"{db_name}:{scene_name}:{len(l)}")
                else:
                    self.subwindow_scenes[key] = [w]

    def _updateSubWindowActions(self : Self) -> None:
        m = hub.main_window
        self.subwindow_actions = {}
        for w in self.subWindowList():
            key = "_"
            if isinstance(w, DrawingSubWindow) \
            and isinstance(w.widget(), DrawingView) \
            and isinstance(w.widget().scene(), Drawing):
                key = id(hub.model.getDbItemFromScene(w.widget().scene()))
            action = Action(m, w.windowTitle(), None, None, False, False, w)
            action.triggered.connect(
                lambda checked=False, sw=w: self._activateSubWindow(sw)
            )
            if key in self.subwindow_actions:
                self.subwindow_actions[key].append(action)
            else:
                self.subwindow_actions[key] = [action]

    def _activateSubWindowIndexOffset(self : Self, offset : int) -> None:
        windows = self.subWindowList()
        if not windows:
            return
        current_window = self.activeSubWindow()
        if not current_window:
            self.setActiveSubWindow(windows[0])
            return
        current_index = windows.index(current_window)
        next_index = (current_index + offset) % len(windows)
        next_window = windows[next_index]
        self._activateSubWindow(next_window)

    def _activateSubWindow(self : Self, subwindow : QMdiSubWindow) -> None:
        super().setActiveSubWindow(subwindow)
        subwindow.show()
        subwindow.raise_()
        subwindow.setFocus()
