from PyQt6.QtWidgets import QWidget

from .tree_view_dock import TreeViewDock
from .explorer    import Explorer


class ExplorerDock(TreeViewDock):
    WINDOW_TITLE = 'Database Explorer'

    explorer : Explorer

    def __init__(self, parent : QWidget) -> None:
        super().__init__(parent, None)
        self.explorer = Explorer(self)
        self.setWidget(self.explorer)
