from PyQt6.QtWidgets import QDockWidget, QWidget

from .tree_view import TreeView


class TreeViewDock(QDockWidget):
    WINDOW_TITLE = 'Tree Viewer'

    def __init__(
        self   : 'TreeViewDock',
        parent : QWidget,
        widget : TreeView
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setWidget(widget)
