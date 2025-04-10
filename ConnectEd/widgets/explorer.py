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
        a.copy = QAction('Copy', self)
        a.copy.triggered.connect(lambda: self.copy(self.item))
        a.paste = QAction('Paste', self)
        a.paste.triggered.connect(lambda: self.paste(self.item))

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
            new_action = self.actions.newItem
            open_action = self.actions.openItem
            new_window_action = self.actions.newWindow
            edit_action = self.actions.editDrawing
            save_action = self.actions.saveDb
            save_as_action = self.actions.saveAsDb
            close_action = self.actions.closeDb
            self.item = self.model().itemFromIndex(index)
            item = self.model().itemFromIndex(index)
            match hub.db_model.getItemTypeStr(item):
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
                    menu.addAction(save_action)
                    menu.addAction(save_as_action)
                    menu.addAction(close_action)
                case 'Library':
                    new_action.setText('New Symbol')
                    save_action.setText('Save Library')
                    save_as_action.setText('Save Library As')
                    close_action.setText('Close Library')
                    menu.addAction(new_action)
                    menu.addAction(save_action)
                    menu.addAction(save_as_action)
                    menu.addAction(close_action)
                case 'Diagrams':
                    new_action.setText('New Diagram')
                    menu.addAction(new_action)
                case 'Symbol Cache':
                    new_action.setText('New Symbol')
                    menu.addAction(self.actions.newItem)
                case 'Diagram':
                    edit_action.setText('Edit Diagram')
                    new_window_action.setText('New Diagram Window')
                    menu.addAction(edit_action)
                    menu.addAction(new_window_action)
                case 'Symbol':
                    edit_action.setText('Edit Symbol')
                    new_window_action.setText('New Symbol Window')
                    menu.addAction(edit_action)
                    menu.addAction(new_window_action)
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

    def newWindow(self : 'Explorer', item : 'DrawingItem') -> None:
        hub.db_model.newWindow(item)

    def editDrawing(self : 'Explorer', item : 'DrawingItem') -> None:
        hub.db_model.editDrawing(item)

    def saveDb(self : 'Explorer', item : QStandardItem) -> None:
        hub.db_model.saveDb(item)

    def saveAsDb(self : 'Explorer', item : QStandardItem) -> None:
        hub.db_model.saveAsDb(item)

    def closeDb(self : 'Explorer', item : QStandardItem) -> None:
        hub.db_model.closeDb(item)

    def copy(self : 'Explorer', item : QStandardItem) -> None:
        hub.db_model.copy(item)

    def paste(self : 'Explorer', item : QStandardItem) -> None:
        hub.db_model.paste(item)
