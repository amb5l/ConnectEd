from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QMdiArea, QWidget
from PyQt6.QtGui     import QAction

from ...app import logger,model, window

from ..action import Action

from .sub_window  import SubWindow
from .spreadsheet import SpreadsheetSubWindow

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...widgets.graphics.scenes.drawing import DrawingScene


class MdiArea(QMdiArea):
    _scene_subwindow_actions : dict["DrawingScene", list[Action]]

    def __init__(self : Self) -> None:
        super().__init__()
        self._scene_subwindow_actions = {}

    def addSubWindow(
        self      : Self,
        subwindow : QWidget,
        flags     : Qt.WindowType = Qt.WindowType.SubWindow
    ) -> None:
        super().addSubWindow(subwindow, flags)
        if isinstance(subwindow, SubWindow):
            # Connect to destroyed signal to update menu when window is closed
            subwindow.destroyed.connect(self.update)
        self.update()

    def nextSubWindow(self : Self) -> None:
        self._activateSubWindowIndexOffset(1)

    def previousSubWindow(self : Self) -> None:
        self._activateSubWindowIndexOffset(-1)

    def update(self : Self) -> None:
        self._updateSubWindows()
        window().menu_bar.updateWindowMenu()

    def activateSubWindow(self : Self, subwindow : SubWindow) -> None:
        super().setActiveSubWindow(subwindow)
        subwindow.show()
        subwindow.raise_()
        subwindow.setFocus()

    def sceneSubWindows(self : Self, scene : "DrawingScene") -> list[SubWindow]:
        """Return all scene subwindows in top down Z order."""
        r = []
        for w in reversed(self.subWindowList()):
            if hasattr(w, "scene") and w.scene() == scene:
                r.append(w)
        return r

    def scenesActions(self : Self) -> dict["DrawingScene", list[Action]]:
        return self._scene_subwindow_actions

    def closeScene(self : Self, scene : "DrawingScene") -> None:
        """Close all subwindows related to the specified scene."""
        for w in self.subWindowList():
            if hasattr(w, "scene") and w.scene() == scene:
                w.close()

    def _updateSubWindows(self : Self) -> None:
        from ...widgets.graphics.scenes.diagram import DiagramScene
        from ...widgets.graphics.scenes.symbol  import SymbolScene
        from ...widgets.graphics.views.drawing  import DrawingSubWindow
        # create dictionaries
        scene_subwindows : dict["DrawingScene" | None, list[SubWindow]] = {}
        self._scene_subwindow_actions = {}
        # build scene => subwindow list dictionary
        for w in self.subWindowList():
            if isinstance(w, SubWindow):
                if hasattr(w, "scene"):
                    scene = w.scene()
                    scene_subwindows.setdefault(scene, []).append(w)
                else:
                    logger().warning(f"Subwindow {w} has no scene method")
        # set titles
        for scene in scene_subwindows.keys():
            if scene is None:
                continue
            # get DB name
            db_node = model().getDbNodeFromScene(scene)
            if db_node is None:
                logger().warning(f"No db node found for scene: {scene}")
                db_name = "???"
            else:
                db_name = db_node.text()
            # build lists of subwindows
            drawing_subwindows : list[DrawingSubWindow] = []
            spreadsheet_subwindows : list[SpreadsheetSubWindow] = []
            for w in scene_subwindows[scene]:
                if isinstance(w, DrawingSubWindow):
                    drawing_subwindows.append(w)
                elif isinstance(w, SpreadsheetSubWindow):
                    spreadsheet_subwindows.append(w)
            # drawing subwindow titles and actions
            for i, w in enumerate(drawing_subwindows):
                if isinstance(scene, DiagramScene):
                    title = f"{db_name} - Diagram Editor"
                elif isinstance(scene, SymbolScene):
                    title = f"{db_name}:{scene.name()} - Symbol Editor"
                else:
                    title = f"{db_name}:{scene.name()} - Drawing Editor"
                suffix = "" if len(drawing_subwindows) == 1 else f" ({i + 1})"
                w.setWindowTitle(title + suffix)
                action = QAction(window())
                action.setText(title + suffix)
                def showSubWindow(checked=False, window=w) -> None:
                    window.show()
                    window.raise_()
                    window.setFocus()
                action.triggered.connect(showSubWindow)
                self._scene_subwindow_actions.setdefault(scene, []).append(action)
            # spreadsheet subwindow titles and actions
            for i, w in enumerate(spreadsheet_subwindows):
                if isinstance(scene, DiagramScene):
                    title = f"{db_name} - Diagram Properties"
                elif isinstance(scene, SymbolScene):
                    title = f"{db_name}:{scene.name()} - Symbol Properties"
                else:
                    title = f"{db_name}:{scene.name()} - Drawing Properties"
                suffix = "" if len(spreadsheet_subwindows) == 1 else f" ({i + 1})"
                w.setWindowTitle(title + suffix)
                action = QAction(window())
                action.setText(title + suffix)
                def showSubWindow(checked=False, window=w) -> None:
                    window.show()
                    window.raise_()
                    window.setFocus()
                action.triggered.connect(showSubWindow)
                self._scene_subwindow_actions.setdefault(scene, []).append(action)

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
        self.activateSubWindow(next_window)
