from PyQt6.QtWidgets import QWidget

from .tree_view import TreeView

from .. import hub

class DbExplorer(TreeView):
    def __init__(self, parent : QWidget) -> None:
        super().__init__(parent, hub.database_manager.get_model())
