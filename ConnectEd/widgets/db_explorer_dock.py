from PyQt6.QtWidgets import QWidget

from .tree_view_dock import TreeViewDock
from .db_explorer    import DbExplorer


class DbExplorerDock(TreeViewDock):
    WINDOW_TITLE = 'Database Explorer'

    def __init__(self, parent : QWidget) -> None:
        super().__init__(parent, None)
        self.db_explorer = DbExplorer(self)
        self.setWidget(self.db_explorer)
