import re

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QMdiArea, QWidget, QMdiSubWindow

from ..private import Action
from ..views   import DrawingSubWindow, DrawingView
from ..scenes  import DrawingScene

from ... import hub

class MdiArea(QMdiArea):
    subwindow_actions : dict[any, list[Action]]
    subwindow_scenes  : dict[any, list[QMdiSubWindow]]

    def addSubWindow(
        self   : 'MdiArea',
        widget : QWidget,
        flags  : Qt.WindowType = Qt.WindowType.SubWindow
    ) -> None:
        super().addSubWindow(widget, flags)
        if not isinstance(widget, DrawingSubWindow):
            return
        if not isinstance(widget.widget(), DrawingView):
            return
        if not isinstance(widget.widget().scene(), DrawingScene):
            return
        self._update()
        hub.main_window.menu_bar.updateWindowMenu()

    def nextSubWindow(self : 'MdiArea') -> None:
        self._activateSubWindowIndexOffset(1)

    def previousSubWindow(self : 'MdiArea') -> None:
        self._activateSubWindowIndexOffset(-1)

    def _update(self : 'MdiArea') -> None:
        m = hub.main_window
        # update scenes vs subwindows dict
        self.subwindow_scenes = {}
        for w in self.subWindowList():
            key = '_'
            if isinstance(w, DrawingSubWindow) \
            and isinstance(w.widget(), DrawingView) \
            and isinstance(w.widget().scene(), DrawingScene):
                key = id(w.widget().scene())
            if key in self.subwindow_scenes:
                self.subwindow_scenes[key].append(w)
            else:
                self.subwindow_scenes[key] = [w]
        # add numbers to titles of sibling subwindows (showing same scene)
        for key, subwindows in self.subwindow_scenes.items():
            if key == '_':
                continue
            for i, w in enumerate(subwindows):
                title = re.sub(r'\(\d+\)$', '', w.windowTitle()).strip()
                if len(subwindows) > 1:
                    title = f'{title} ({i + 1})'
                w.setWindowTitle(title)
        # update db vs actions dict
        self.subwindow_actions = {}
        for w in self.subWindowList():
            key = '_'
            if isinstance(w, DrawingSubWindow) \
            and isinstance(w.widget(), DrawingView) \
            and isinstance(w.widget().scene(), DrawingScene):
                key = id(hub.db_model.getDbItemFromScene(w.widget().scene()))
            action = Action(m, w.windowTitle(), None, None, False, False, w)
            action.triggered.connect(
                lambda checked=False, sw=w: self._activateSubWindow(sw)
            )
            if key in self.subwindow_actions:
                self.subwindow_actions[key].append(action)
            else:
                self.subwindow_actions[key] = [action]

    def _activateSubWindowIndexOffset(self : 'MdiArea', offset : int) -> None:
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

    def _activateSubWindow(self : 'MdiArea', subwindow : QMdiSubWindow) -> None:
        super().setActiveSubWindow(subwindow)
        subwindow.show()
        subwindow.raise_()
        subwindow.setFocus()
