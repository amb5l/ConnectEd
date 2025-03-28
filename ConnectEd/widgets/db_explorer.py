from types import SimpleNamespace

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtGui     import QAction, QStandardItem, QWheelEvent, QMouseEvent

from ..core import DbItem, LibraryItem, DiagramItem

from .tree_view import TreeView
from .scenes    import DiagramScene
from .views     import DiagramView, DiagramSubWindow

from .. import hub


class DbExplorer(TreeView):
    actions : SimpleNamespace
    item    : QStandardItem

    def __init__(self, parent : QWidget) -> None:
        super().__init__(parent, hub.db_model)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.actions = SimpleNamespace()
        a = self.actions
        a.increase_text_size = QAction('Increase Text Size', self)
        a.increase_text_size.triggered.connect(self.increase_font_size)
        a.decrease_text_size = QAction('Decrease Text Size', self)
        a.decrease_text_size.triggered.connect(self.decrease_font_size)
        a.new_design = QAction('New', self)
        a.new_design.triggered.connect(self.new_design)
        a.new_diagram = QAction('New', self)
        a.new_diagram.triggered.connect(lambda: self.new_diagram(self.item))
        a.edit_diagram = QAction('Edit', self)
        a.edit_diagram.triggered.connect(lambda: self.edit_diagram(self.item))
        a.new_window = QAction('New Window', self)
        a.new_window.triggered.connect(lambda: self.new_window(self.item))
        a.new_library = QAction('New', self)
        a.new_library.triggered.connect(self.new_library)
        a.save_db = QAction('Save', self)
        a.save_db.triggered.connect(lambda: self.save_db(self.item))
        a.close_db = QAction('Close', self)
        a.close_db.triggered.connect(lambda: self.close_db(self.item))

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle mouse wheel events to adjust font size when Ctrl is pressed."""
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.increase_font_size()
            elif delta < 0:
                self.decrease_font_size()
            event.accept()
            return
        super().wheelEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Handle double-click."""
        if event.button() == Qt.MouseButton.LeftButton:
            index = self.indexAt(event.pos())
            if index.isValid():
                item = self.model().itemFromIndex(index)
                parent_item = item.parent()
                if (item.text() == 'Designs') \
                or (item.text() == 'Libraries') \
                or (parent_item and parent_item.text() == 'Designs') \
                or (parent_item and parent_item.text() == 'Libraries') \
                or (item.text() == 'Diagrams') \
                or (item.text() == 'Symbol Cache'):
                    self.setExpanded(index, not self.isExpanded(index))
                    event.accept()
                    return
                elif parent_item and parent_item.text() == 'Diagrams':
                    self.edit_diagram(item)
                    event.accept()
                    return
        super().mouseDoubleClickEvent(event)

    def show_context_menu(self, pos) -> None:
        menu = QMenu(self)
        index = self.indexAt(pos)
        if index.isValid():
            self.item = self.model().itemFromIndex(index)
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
                menu.addAction(self.actions.new_window)
            menu.addSeparator()
        menu.addAction(self.actions.increase_text_size)
        menu.addAction(self.actions.decrease_text_size)
        menu.exec(self.viewport().mapToGlobal(pos))

    def new_design(self : 'DbExplorer') -> None:
        hub.db_model.new_design()

    def new_diagram(self : 'DbExplorer', item : DiagramItem) -> None:
        item.appendRow(DiagramItem())

    def edit_diagram(self : 'DbExplorer', item : DiagramItem) -> None:
        hub.db_model.edit_diagram(item)

    def new_library(self : 'DbExplorer') -> None:
        hub.db_model.new_library()

    def new_window(self : 'DbExplorer', item : DiagramItem) -> None:
        hub.db_model.new_window(item)

    def save_db(self : 'DbExplorer', item : QStandardItem) -> None:
        hub.db_model.save(item)

    def close_db(self : 'DbExplorer', item : QStandardItem) -> None:
        hub.db_model.close(item)
