from types import SimpleNamespace

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtGui     import QAction, QStandardItem, QWheelEvent, QMouseEvent

from .tree_view import TreeView

from .. import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..core import DrawingItem


class DbExplorer(TreeView):
    actions : SimpleNamespace
    item    : QStandardItem

    def __init__(self, parent : QWidget) -> None:
        super().__init__(parent, hub.db_model)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.actions = SimpleNamespace()
        a = self.actions
        a.increaseTextSize = QAction('Increase Text Size', self)
        a.increaseTextSize.triggered.connect(self.increaseFontSize)
        a.decreaseTextSize = QAction('Decrease Text Size', self)
        a.decreaseTextSize.triggered.connect(self.decreaseFontSize)
        a.newItem = QAction('New', self)
        a.newItem.triggered.connect(lambda: self.newItem(self.item))
        a.editDrawing = QAction('Edit', self)
        a.editDrawing.triggered.connect(lambda: self.editDrawing(self.item))
        a.newWindow = QAction('New Window', self)
        a.newWindow.triggered.connect(lambda: self.newWindow(self.item))
        a.saveDb = QAction('Save', self)
        a.saveDb.triggered.connect(lambda: self.saveDb(self.item))
        a.saveAsDb = QAction('Save As', self)
        a.saveAsDb.triggered.connect(lambda: self.saveAsDb(self.item))
        a.closeDb = QAction('Close', self)
        a.closeDb.triggered.connect(lambda: self.closeDb(self.item))

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle mouse wheel events to adjust font size when Ctrl is pressed."""
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.increaseFontSize()
            elif delta < 0:
                self.decreaseFontSize()
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
                    self.editDrawing(item)
                    event.accept()
                    return
        super().mouseDoubleClickEvent(event)

    def showContextMenu(self, pos) -> None:
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
                menu.addAction(self.actions.newItem)
            elif item.text() == 'Libraries':
                # item is Libraries collection
                menu.addAction(self.actions.newItem)
            elif parent_item and parent_item.text() == 'Designs':
                # item is a design
                menu.addAction(self.actions.saveDb)
                menu.addAction(self.actions.saveAsDb)
                menu.addAction(self.actions.closeDb)
            elif parent_item and parent_item.text() == 'Libraries':
                # item is a library
                menu.addAction(self.actions.newItem)
                menu.addAction(self.actions.saveDb)
                menu.addAction(self.actions.saveAsDb)
                menu.addAction(self.actions.closeDb)
            elif item.text() == 'Diagrams':
                # item is a Design's Diagrams collection
                menu.addAction(self.actions.newItem)
            elif parent_item.text() == 'Diagrams':
                # item is a Diagram
                menu.addAction(self.actions.editDrawing)
                menu.addAction(self.actions.newWindow)
            elif grandparent_item.text() == 'Libraries':
                # item is a symbol
                menu.addAction(self.actions.editDrawing)
                menu.addAction(self.actions.newWindow)
            menu.addSeparator()
        menu.addAction(self.actions.increaseTextSize)
        menu.addAction(self.actions.decreaseTextSize)
        menu.exec(self.viewport().mapToGlobal(pos))

    def newWindow(self : 'DbExplorer', item : 'DrawingItem') -> None:
        hub.db_model.newWindow(item)

    def newItem(self : 'DbExplorer', item : QStandardItem) -> None:
        hub.db_model.newItem(item)

    def editDrawing(self : 'DbExplorer', item : 'DrawingItem') -> None:
        hub.db_model.editDrawing(item)

    def saveDb(self : 'DbExplorer', item : QStandardItem) -> None:
        hub.db_model.saveDb(item)

    def saveAsDb(self : 'DbExplorer', item : QStandardItem) -> None:
        hub.db_model.saveAsDb(item)

    def closeDb(self : 'DbExplorer', item : QStandardItem) -> None:
        hub.db_model.closeDb(item)
