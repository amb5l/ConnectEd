from types import SimpleNamespace

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtGui     import QAction, QStandardItem

from ..core import DbItem, LibraryItem, DiagramItem

from .tree_view import TreeView
from .scenes    import DiagramScene
from .views     import DiagramView, DiagramSubWindow

from .. import hub


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
        self.actions.new_design = QAction('New', self)
        self.actions.new_design.triggered.connect(self.new_design)
        self.actions.new_diagram = QAction('New', self)
        self.actions.new_diagram.triggered.connect(lambda: self.new_diagram(self.ctx_item))
        self.actions.edit_diagram = QAction('Edit', self)
        self.actions.edit_diagram.triggered.connect(lambda: self.edit_diagram(self.ctx_item))
        self.actions.new_library = QAction('New', self)
        self.actions.new_library.triggered.connect(self.new_library)
        self.actions.save_db = QAction('Save', self)
        self.actions.save_db.triggered.connect(lambda: self.save_db(self.ctx_item))
        self.actions.close_db = QAction('Close', self)
        self.actions.close_db.triggered.connect(lambda: self.close_db(self.ctx_item))

    def show_context_menu(self, pos):
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
                menu.addAction(self.actions.save_db)
                menu.addAction(self.actions.close_db)
            elif parent_item and parent_item.text() == 'Libraries':
                menu.addAction(self.actions.save_db)
                menu.addAction(self.actions.close_db)
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
        hub.db_model.new_design()

    def new_diagram(self : 'DbExplorer', item: QStandardItem):
        item.appendRow(DiagramItem())

    def edit_diagram(self : 'DbExplorer', item: QStandardItem) -> None:
        design_item = item.parent().parent()
        diagram_name = item.text()
        diagram_scene : DiagramScene = item.data(Qt.ItemDataRole.UserRole)
        subwindow = DiagramSubWindow()
        diagram_view = DiagramView(diagram_scene)
        subwindow.setWidget(diagram_view)
        subwindow.setWindowTitle(f'{design_item.text()}: {diagram_name}')
        hub.main_window.mdi_area.addSubWindow(subwindow)
        subwindow.showMaximized()
        hub.main_window.menu_bar.updateWindowMenu()

    def new_library(self : 'DbExplorer'):
        hub.db_model.libraries.appendRow(LibraryItem())

    def save_db(self : 'DbExplorer', item: 'DbItem'):
        hub.db_model.save(item)

    def close_db(self : 'DbExplorer', item: 'DbItem'):
        hub.db_model.close(item)

