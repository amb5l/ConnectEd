from types import SimpleNamespace

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtGui     import QAction, QStandardItem, QWheelEvent, QMouseEvent

from .tree_view import TreeView

from .. import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..core import DrawingItem


class Explorer(TreeView):
    actions : SimpleNamespace
    item    : QStandardItem

    def __init__(self, parent : QWidget) -> None:
        super().__init__(parent, hub.db_model)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.setEditTriggers(
            self.EditTrigger.SelectedClicked |
            self.EditTrigger.EditKeyPressed  |
            self.EditTrigger.DoubleClicked
        )
        self.actions = SimpleNamespace()
        a = self.actions
        a.increaseTextSize = QAction('Increase Text Size', self)
        a.increaseTextSize.triggered.connect(self.increaseFontSize)
        a.decreaseTextSize = QAction('Decrease Text Size', self)
        a.decreaseTextSize.triggered.connect(self.decreaseFontSize)
        a.newItem = QAction('New', self)
        a.newItem.triggered.connect(lambda: self.newItem(self.item))
        a.openItem = QAction('Open', self)
        a.openItem.triggered.connect(lambda: self.openItem(self.item))
        a.editItem = QAction('Edit', self)
        a.editItem.triggered.connect(lambda: self.editItem(self.item))
        a.newItemWindow = QAction('New Window', self)
        a.newItemWindow.triggered.connect(lambda: self.newItemWindow(self.item))
        a.saveItem = QAction('Save', self)
        a.saveItem.triggered.connect(lambda: self.saveItem(self.item))
        a.saveAsItem = QAction('Save As', self)
        a.saveAsItem.triggered.connect(lambda: self.saveAsItem(self.item))
        a.closeItem = QAction('Close', self)
        a.closeItem.triggered.connect(lambda: self.closeItem(self.item))
        a.copy = QAction('Copy', self)
        a.copy.triggered.connect(lambda: self.copy(self.item))
        a.paste = QAction('Paste', self)
        a.paste.triggered.connect(lambda: self.paste(self.item))
        a.rename = QAction('Rename', self)
        a.rename.triggered.connect(self.renameSelectedItem)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press to deselect items when clicking in empty space."""
        index = self.indexAt(event.pos())
        if not index.isValid() and event.button() == Qt.MouseButton.LeftButton:
            self.clearSelection()
            self.setCurrentIndex(self.model().index(-1, -1))  # invalid index
            event.accept()
            return
        super().mousePressEvent(event)

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
                    self.editItem(item)
                    event.accept()
                    return
        super().mouseDoubleClickEvent(event)

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

    def renameSelectedItem(self) -> None:
        """Start editing the selected item's text."""
        from ..core import DbItem, DrawingItem
        if self.currentIndex().isValid():
            item = self.model().itemFromIndex(self.currentIndex())
            if isinstance(item, DbItem) \
            or isinstance(item, DrawingItem):
                self.edit(self.currentIndex())

    def showContextMenu(self, pos) -> None:
        menu = QMenu(self)
        index = self.indexAt(pos)
        if not index.isValid(): # if clicking in empty space
            index = self.currentIndex()
        if index.isValid():
            new_action        = self.actions.newItem
            open_action       = self.actions.openItem
            new_window_action = self.actions.newItemWindow
            edit_action       = self.actions.editItem
            save_action       = self.actions.saveItem
            save_as_action    = self.actions.saveAsItem
            close_action      = self.actions.closeItem
            rename_action     = self.actions.rename
            self.item = self.model().itemFromIndex(index)
            item = self.model().itemFromIndex(index)
            match hub.db_model.getItemTypeName(item):
                case 'Designs':
                    new_action.setText('New Design')
                    open_action.setText('Open Design')
                    menu.addAction(new_action)
                    menu.addAction(open_action)
                case 'Libraries':
                    new_action.setText('New Library')
                    open_action.setText('Open Library')
                    menu.addAction(new_action)
                    menu.addAction(open_action)
                case 'Design':
                    save_action.setText('Save Design')
                    save_as_action.setText('Save Design As')
                    close_action.setText('Close Design')
                    rename_action.setText('Rename Design')
                    menu.addAction(save_action)
                    menu.addAction(save_as_action)
                    menu.addAction(close_action)
                    menu.addSeparator()
                    menu.addAction(rename_action)
                case 'Library':
                    new_action.setText('New Symbol')
                    save_action.setText('Save Library')
                    save_as_action.setText('Save Library As')
                    close_action.setText('Close Library')
                    rename_action.setText('Rename Library')
                    menu.addAction(new_action)
                    menu.addAction(save_action)
                    menu.addAction(save_as_action)
                    menu.addAction(close_action)
                    menu.addSeparator()
                    menu.addAction(rename_action)
                case 'Diagrams':
                    new_action.setText('New Diagram')
                    menu.addAction(new_action)
                case 'Symbol Cache':
                    new_action.setText('New Symbol')
                    menu.addAction(self.actions.newItem)
                case 'Diagram':
                    edit_action.setText('Edit Diagram')
                    new_window_action.setText('New Diagram Window')
                    rename_action.setText('Rename Diagram')
                    menu.addAction(edit_action)
                    menu.addAction(new_window_action)
                    menu.addSeparator()
                    menu.addAction(rename_action)
                case 'Symbol':
                    edit_action.setText('Edit Symbol')
                    new_window_action.setText('New Symbol Window')
                    rename_action.setText('Rename Symbol')
                    menu.addAction(edit_action)
                    menu.addAction(new_window_action)
                    menu.addAction(rename_action)
            menu.addSeparator()
            menu.addAction(self.actions.copy)
            menu.addAction(self.actions.paste)
            menu.addSeparator()
        menu.addAction(self.actions.increaseTextSize)
        menu.addAction(self.actions.decreaseTextSize)
        menu.exec(self.viewport().mapToGlobal(pos))

    def newItem(self : 'Explorer', item : QStandardItem) -> None:
        hub.db_model.newItem(item)

    def openItem(self : 'Explorer', item : QStandardItem) -> None:
        hub.db_model.openItem(item)

    def newItemWindow(self : 'Explorer', item : 'DrawingItem') -> None:
        hub.db_model.newItemWindow(item)

    def editItem(self : 'Explorer', item : 'DrawingItem') -> None:
        hub.db_model.editItem(item)

    def saveItem(self : 'Explorer', item : QStandardItem) -> None:
        hub.db_model.saveItem(item)

    def saveAsItem(self : 'Explorer', item : QStandardItem) -> None:
        hub.db_model.saveAsItem(item)

    def closeItem(self : 'Explorer', item : QStandardItem) -> None:
        hub.db_model.closeItem(item)

    def copy(self : 'Explorer', item : QStandardItem) -> None:
        hub.db_model.copy(item)

    def paste(self : 'Explorer', item : QStandardItem) -> None:
        hub.db_model.paste(item)
