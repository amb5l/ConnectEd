from types import SimpleNamespace

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtGui     import QAction, QStandardItem, QWheelEvent, QMouseEvent

from ..core import DbItem, LibraryItem, DiagramItem, DrawingItem

from .tree_view import TreeView
from .scenes    import DiagramScene
from .views     import DiagramView, DrawingSubWindow

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
        a.new_item = QAction('New', self)
        a.new_item.triggered.connect(lambda: self.new_item(self.item))
        a.edit_item = QAction('Edit', self)
        a.edit_item.triggered.connect(lambda: self.edit_item(self.item))
        a.new_window = QAction('New Window', self)
        a.new_window.triggered.connect(lambda: self.new_window(self.item))
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
                    self.edit_item(item)
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
            grandparent_item = None if parent_item is None else \
                parent_item.parent()
            if item.text() == 'Designs':
                # item is Designs collection
                menu.addAction(self.actions.new_item)
            elif item.text() == 'Libraries':
                # item is Libraries collection
                menu.addAction(self.actions.new_item)
            elif parent_item and parent_item.text() == 'Designs':
                # item is a design
                menu.addAction(self.actions.save_db)
                menu.addAction(self.actions.close_db)
            elif parent_item and parent_item.text() == 'Libraries':
                # item is a library
                menu.addAction(self.actions.new_item)
                menu.addAction(self.actions.save_db)
                menu.addAction(self.actions.close_db)
            elif item.text() == 'Diagrams':
                # item is a Design's Diagrams collection
                menu.addAction(self.actions.new_item)
            elif parent_item.text() == 'Diagrams':
                # item is a Diagram
                menu.addAction(self.actions.edit_item)
                menu.addAction(self.actions.new_window)
            elif grandparent_item.text() == 'Libraries':
                # item is a symbol
                menu.addAction(self.actions.edit_item)
                menu.addAction(self.actions.new_window)
            menu.addSeparator()
        menu.addAction(self.actions.increase_text_size)
        menu.addAction(self.actions.decrease_text_size)
        menu.exec(self.viewport().mapToGlobal(pos))

    def new_window(self : 'DbExplorer', item : DrawingItem) -> None:
        hub.db_model.new_window(item)

    def new_item(self : 'DbExplorer', item : QStandardItem) -> None:
        hub.db_model.new_item(item)

    def edit_item(self : 'DbExplorer', item : DrawingItem) -> None:
        hub.db_model.edit_item(item)

    def save_db(self : 'DbExplorer', item : QStandardItem) -> None:
        hub.db_model.save_db(item)

    def close_db(self : 'DbExplorer', item : QStandardItem) -> None:
        hub.db_model.close_db(item)
