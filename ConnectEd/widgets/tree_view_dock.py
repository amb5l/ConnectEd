from typing import Optional

from PyQt6.QtWidgets import QDockWidget, QWidget

from .tree_view import TreeView


class TreeViewDock(QDockWidget):
    WINDOW_TITLE = 'Tree Viewer'

    def __init__(
        self   : 'TreeViewDock',
        parent : QWidget,
        widget : Optional[TreeView] = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.WINDOW_TITLE)
        if widget is not None:
            self.setWidget(widget)
