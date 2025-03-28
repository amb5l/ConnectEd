from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtGui     import QAction, QStandardItem

from ..core import DesignItem, LibraryItem, DiagramItem

from .tree_view import TreeView
from .scenes    import DiagramScene
from .views     import DiagramView, DiagramSubWindow

from .. import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..core import DesignItem, DiagramItem


class DbExplorer(TreeView):
    def __init__(self, parent : QWidget) -> None:
        super().__init__(parent, hub.db_model)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        """Handle right-click context menu."""
        index = self.indexAt(pos)
        if not index.isValid():
            return
        item = self.model().itemFromIndex(index)
        parent_item = item.parent()
        if item.text() == 'Designs':
            menu = QMenu(self)
            new_action = QAction('New', self)
            new_action.triggered.connect(self.new_design)
            menu.addAction(new_action)
            menu.exec(self.viewport().mapToGlobal(pos))
        elif item.text() == 'Libraries':
            menu = QMenu(self)
            new_library_action = QAction('New', self)
            new_library_action.triggered.connect(self.new_library)
            menu.addAction(new_library_action)
            menu.exec(self.viewport().mapToGlobal(pos))
        elif parent_item and parent_item.text() == 'Designs':
            design = item.data(Qt.ItemDataRole.UserRole)  # retrieve the Design object
            menu = QMenu(self)
            save_action = QAction('Save', self)
            save_action.triggered.connect(lambda: self.save_design(design))
            menu.addAction(save_action)
            close_action = QAction('Close', self)
            close_action.triggered.connect(lambda: self.close_design(design))
            menu.addAction(close_action)
            menu.exec(self.viewport().mapToGlobal(pos))
        elif item.text() == 'Diagrams':
            menu = QMenu(self)
            new_action = QAction('New', self)
            new_action.triggered.connect(lambda: self.new_diagram(item))
            menu.addAction(new_action)
            menu.exec(self.viewport().mapToGlobal(pos))
        elif parent_item and parent_item.text() == 'Diagrams':
            diagram = item.data(Qt.ItemDataRole.UserRole)
            menu = QMenu(self)
            edit_action = QAction('Edit', self)
            edit_action.triggered.connect(
                lambda: self.edit_diagram(item.text(), diagram)
            )
            menu.addAction(edit_action)
            menu.exec(self.viewport().mapToGlobal(pos))

    def new_design(self : 'DbExplorer'):
        """Create a new Design. Add a new Diagram to it."""
        hub.db_model.new_design()

    def save_design(self : 'DbExplorer', design: 'DesignItem'):
        """Save the specified Design."""
        hub.db_model.save(design)

    def close_design(self : 'DbExplorer', design: 'DesignItem'):
        """Close the specified Design and remove it from the tree."""
        hub.db_model.close(design)

    def new_diagram(self : 'DbExplorer', item: QStandardItem):
        """Create a new Diagram in the specified Design."""
        item.appendRow(DiagramItem())

    def edit_diagram(
        self          : 'DbExplorer',
        diagram_name  : str,
        diagram_scene : DiagramScene
    ) -> None:
        """Edit the specified Diagram."""
        subwindow = DiagramSubWindow()
        diagram_view = DiagramView(diagram_scene)
        subwindow.setWidget(diagram_view)
        subwindow.setWindowTitle(diagram_name)
        hub.main_window.mdi_area.addSubWindow(subwindow)
        subwindow.showMaximized()

    def new_library(self : 'DbExplorer'):
        """Create a new Library."""
        hub.db_model.libraries.appendRow(LibraryItem())
