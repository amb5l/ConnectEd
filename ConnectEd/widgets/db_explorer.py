from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtGui     import QAction

from ..core import Design

from .tree_view import TreeView

from .. import hub


class DbExplorer(TreeView):
    def __init__(self, parent : QWidget) -> None:
        super().__init__(parent, hub.database_manager.get_model())
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        """Handle right-click context menu."""
        index = self.indexAt(pos)
        if not index.isValid():
            return
        item = self.model().itemFromIndex(index)
        if item.text() == "Designs":  # Check if the clicked item is "Designs"
            menu = QMenu(self)
            new_design_action = QAction("New Design", self)
            new_design_action.triggered.connect(self.create_new_design)
            menu.addAction(new_design_action)
            menu.exec(self.viewport().mapToGlobal(pos))

    def create_new_design(self):
        """Create a new Design via DatabaseManager."""
        hub.database_manager.new(Design)