from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtGui     import QAction, QStandardItem, QStandardItemModel

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
        parent_item = item.parent()
        # context menu for "Designs"
        if item.text() == "Designs":
            menu = QMenu(self)
            new_design_action = QAction("New Design", self)
            new_design_action.triggered.connect(self.create_new_design)
            menu.addAction(new_design_action)
            menu.exec(self.viewport().mapToGlobal(pos))
        # context menu for individual design nodes
        elif parent_item and parent_item.text() == "Designs":
            design = item.data(Qt.ItemDataRole.UserRole)  # Retrieve the Design object
            if isinstance(design, Design):
                menu = QMenu(self)
                save_action = QAction("Save", self)
                save_action.triggered.connect(lambda: self.save_design(design))
                menu.addAction(save_action)
                close_action = QAction("Close", self)
                close_action.triggered.connect(lambda: self.close_design(design, item))
                menu.addAction(close_action)
                menu.exec(self.viewport().mapToGlobal(pos))


    def create_new_design(self : 'DbExplorer'):
        """Create a new Design via DatabaseManager."""
        hub.database_manager.new(Design)

    def save_design(self : 'DbExplorer', design: Design):
        """Save the specified Design."""
        hub.database_manager.save(design)

    def close_design(self : 'DbExplorer', design: Design, item: QStandardItem):
        """Close the specified Design and remove it from the tree."""
        hub.database_manager.close(design)
