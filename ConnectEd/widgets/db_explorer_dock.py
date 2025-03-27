from PyQt6.QtWidgets import QWidget

from .tree_view_dock import TreeViewDock
from .db_explorer    import DbExplorer


class DbExplorerDock(TreeViewDock):
    WINDOW_TITLE = 'Database Explorer'

    def __init__(self, parent : QWidget) -> None:
        db_explorer = DbExplorer(parent)
        super().__init__(parent, db_explorer)
