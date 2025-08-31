from typing import Self

from PyQt6.QtCore    import Qt, QChildEvent, QEvent
from PyQt6.QtWidgets import QMdiArea, QWidget, QMdiSubWindow

from ..private import Action

from ...widgets.graphics.views.drawing import DrawingSubWindow, DrawingView

from ...widgets.graphics.scenes.drawing import DrawingScene

from .spreadsheet import SpreadsheetSubWindow

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
        if isinstance(widget, DrawingSubWindow):
            if not isinstance(widget.widget(), DrawingView):
                return
            if not isinstance(widget.widget().scene(), DrawingScene):
                return
            self.update()
        elif isinstance(widget, SpreadsheetSubWindow):
            if widget.scene() is not None:
                self.update()

    def nextSubWindow(self : Self) -> None:
        self._activateSubWindowIndexOffset(1)

    def previousSubWindow(self : Self) -> None:
        self._activateSubWindowIndexOffset(-1)

    def update(self : Self) -> None:
        self._updateSubWindowTitles()
        self._updateSubWindowActions()
        hub.window.menu_bar.updateWindowMenu()

    def childEvent(self : Self, event : QChildEvent) -> None:
        """Handle child events, particularly when subwindows are removed."""
        super().childEvent(event)
        if (event.type() == QEvent.Type.ChildRemoved and
            isinstance(event.child(), QMdiSubWindow)):
            self.update()

    def _updateSubWindowTitles(self : Self) -> None:
        self.subwindow_scenes = {}
        for w in self.subWindowList():
            # skip windows that are closing or closed
            if w.isHidden():
                continue
            if isinstance(w, DrawingSubWindow) and not w.widget():
                continue
            scene = None
            if isinstance(w, DrawingSubWindow) \
            and isinstance(w.widget(), DrawingView) \
            and isinstance(w.widget().scene(), DrawingScene):
                scene = w.widget().scene()
            elif isinstance(w, SpreadsheetSubWindow) and w.scene() is not None:
                scene = w.scene()
            if scene is not None:
                key = id(scene)
                if key in self.subwindow_scenes:
                    self.subwindow_scenes[key].append(w)
                else:
                    self.subwindow_scenes[key] = [w]
        for key, windows in self.subwindow_scenes.items():
            if not windows:
                continue
            scene = None
            for w in windows:
                if isinstance(w, DrawingSubWindow) and isinstance(w.widget(), DrawingView):
                    scene = w.widget().scene()
                    break
                elif isinstance(w, SpreadsheetSubWindow):
                    scene = w.scene()
                    break
            if scene is None:
                continue
            scene_name = scene.item.text()
            db_name = hub.model.getDbItemFromScene(scene).text()
            properties_windows = [w for w in windows if isinstance(w, SpreadsheetSubWindow)]
            drawing_windows = [w for w in windows if isinstance(w, DrawingSubWindow)]
            sorted_windows = properties_windows + drawing_windows
            if len(sorted_windows) == 1:
                if isinstance(sorted_windows[0], SpreadsheetSubWindow):
                    sorted_windows[0].setWindowTitle(f"{db_name}:{scene_name}: Properties")
                else:
                    sorted_windows[0].setWindowTitle(f"{db_name}:{scene_name}")
            else:
                properties_count = len(properties_windows)
                drawing_count = len(drawing_windows)
                for w in properties_windows:
                    w.setWindowTitle(f"{db_name}:{scene_name}: Properties")
                if drawing_count == 1:
                    drawing_windows[0].setWindowTitle(f"{db_name}:{scene_name}")
                else:
                    for i, w in enumerate(drawing_windows):
                        w.setWindowTitle(f"{db_name}:{scene_name}:{i}")

    def _updateSubWindowActions(self : Self) -> None:
        m = hub.window
        self.subwindow_actions = {}
        for w in self.subWindowList():
            key = "_"
            if isinstance(w, DrawingSubWindow) \
            and isinstance(w.widget(), DrawingView) \
            and isinstance(w.widget().scene(), DrawingScene):
                key = id(hub.model.getDbItemFromScene(w.widget().scene()))
            elif isinstance(w, SpreadsheetSubWindow) and w.scene() is not None:
                key = id(hub.model.getDbItemFromScene(w.scene()))
            action = Action(m, w.windowTitle(), None, None, False, False, w)
            action.triggered.connect(
                lambda checked=False, sw=w: self._activateSubWindow(sw)
            )
            if key in self.subwindow_actions:
                self.subwindow_actions[key].append(action)
            else:
                self.subwindow_actions[key] = [action]
        for key, actions in self.subwindow_actions.items():
            if key == "_":
                continue
            properties_actions = [a for a in actions if isinstance(a.data(), SpreadsheetSubWindow)]
            drawing_actions = [a for a in actions if isinstance(a.data(), DrawingSubWindow)]
            self.subwindow_actions[key] = properties_actions + drawing_actions

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
