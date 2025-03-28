from types import SimpleNamespace

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
    actions   : SimpleNamespace
    ctx_item : QStandardItem


    def __init__(self, parent : QWidget) -> None:
        super().__init__(parent, hub.db_model)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.actions = SimpleNamespace()
        self.actions.increase_text_size = QAction('Increase Text Size', self)
        self.actions.increase_text_size.triggered.connect(self.increase_font_size)
        self.actions.decrease_text_size = QAction('Decrease Text Size', self)
        self.actions.decrease_text_size.triggered.connect(self.decrease_font_size)
        self.actions.new_design = QAction('New Design', self)
        self.actions.new_design.triggered.connect(self.new_design)
        self.actions.save_design = QAction('Save Design', self)
        self.actions.save_design.triggered.connect(lambda: self.save_design(self.ctx_item))
        self.actions.close_design = QAction('Close Design', self)
        self.actions.close_design.triggered.connect(lambda: self.close_design(self.ctx_item))
        self.actions.new_diagram = QAction('New Diagram', self)
        self.actions.new_diagram.triggered.connect(lambda: self.new_diagram(self.ctx_item))
        self.actions.edit_diagram = QAction('Edit Diagram', self)
        self.actions.edit_diagram.triggered.connect(lambda: self.edit_diagram(self.ctx_item))
        self.actions.new_library = QAction('New Library', self)
        self.actions.new_library.triggered.connect(self.new_library)

    def show_context_menu(self, pos):
        """Handle right-click context menu."""
        menu = QMenu(self)
        index = self.indexAt(pos)
        if index.isValid():
            self.ctx_item = self.model().itemFromIndex(index)
            item = self.model().itemFromIndex(index)
            parent_item = item.parent()
            if item.text() == 'Designs':
                menu.addAction(self.actions.new_design)
            elif item.text() == 'Libraries':
                menu.addAction(self.actions.new_library)
            elif parent_item and parent_item.text() == 'Designs':
                menu.addAction(self.actions.save_design)
                menu.addAction(self.actions.close_design)
            elif item.text() == 'Diagrams':
                menu.addAction(self.actions.new_diagram)
                menu.addAction(self.actions.edit_diagram)
            elif parent_item and parent_item.text() == 'Diagrams':
                menu.addAction(self.actions.edit_diagram)
            menu.addSeparator()
        menu.addAction(self.actions.increase_text_size)
        menu.addAction(self.actions.decrease_text_size)
        menu.exec(self.viewport().mapToGlobal(pos))

    def new_design(self : 'DbExplorer'):
        """Create a new Design. Add a new Diagram to it."""
        hub.db_model.new_design()

    def save_design(self : 'DbExplorer', item: 'DesignItem'):
        """Save the specified Design."""
        design : DesignItem = item.data(Qt.ItemDataRole.UserRole)
        hub.db_model.save(design)

    def close_design(self : 'DbExplorer', item: 'DesignItem'):
        """Close the specified Design and remove it from the tree."""
        design : DesignItem = item.data(Qt.ItemDataRole.UserRole)
        hub.db_model.close(design)

    def new_diagram(self : 'DbExplorer', item: QStandardItem):
        """Create a new Diagram in the specified Design."""
        item.appendRow(DiagramItem())

    def edit_diagram(self : 'DbExplorer', item: QStandardItem) -> None:
        """Edit the specified Diagram."""
        diagram_name = item.text()
        diagram_scene : DiagramScene = item.data(Qt.ItemDataRole.UserRole)
        subwindow = DiagramSubWindow()
        diagram_view = DiagramView(diagram_scene)
        subwindow.setWidget(diagram_view)
        subwindow.setWindowTitle(diagram_name)
        hub.main_window.mdi_area.addSubWindow(subwindow)
        subwindow.showMaximized()

    def new_library(self : 'DbExplorer'):
        """Create a new Library."""
        hub.db_model.libraries.appendRow(LibraryItem())
