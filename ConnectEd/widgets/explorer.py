from types import SimpleNamespace

from PyQt6.QtCore    import Qt, QPoint
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtGui     import QAction, QStandardItem, QWheelEvent, QMouseEvent

from ..core import logger

from .tree_view import TreeView

from .. import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..core import DrawingItem, DbItem


class Explorer(TreeView):
    actions : SimpleNamespace
    item    : QStandardItem

    def __init__(self : 'Explorer', parent : QWidget) -> None:
        super().__init__(parent, hub.model)
        hub.model.itemChanged.connect(self.onItemChanged)
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
        a.newDesign = QAction('New Design', self)
        a.newDesign.triggered.connect(self.newDesign)
        a.newLibrary = QAction('New Library', self)
        a.newLibrary.triggered.connect(self.newLibrary)
        a.newDiagram = QAction('New Diagram', self)
        a.newDiagram.triggered.connect(lambda: self.newDiagram(self.item))
        a.newSymbol = QAction('New Symbol', self)
        a.newSymbol.triggered.connect(lambda: self.newSymbol(self.item))
        a.openDesign = QAction('Open Design', self)
        a.openDesign.triggered.connect(lambda: self.open('Design'))
        a.openLibrary = QAction('Open Library', self)
        a.openLibrary.triggered.connect(lambda: self.open('Library'))
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

    def onItemChanged(self : 'Explorer', item : QStandardItem) -> None:
        """Handle changes to items in the model, such as renaming."""
        if item.parent() and item.parent().text() in ('Diagrams', 'Symbol Cache'):
            scene = item.data(Qt.ItemDataRole.UserRole)
            if scene:
                scene.name = item.text()
        hub.main_window.mdi_area.update()

    def mousePressEvent(self : 'Explorer', event: QMouseEvent) -> None:
        """Handle mouse press to deselect items when clicking in empty space."""
        index = self.indexAt(event.pos())
        if not index.isValid() and event.button() in \
            [Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton]:
            self.clearSelection()
            self.setCurrentIndex(self.model().index(-1, -1))  # invalid index
            if event.button() == Qt.MouseButton.LeftButton:
                event.accept()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self : 'Explorer', event: QMouseEvent) -> None:
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

    def wheelEvent(self : 'Explorer', event: QWheelEvent) -> None:
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

    def renameSelectedItem(self : 'Explorer') -> None:
        """Start editing the selected item's text."""
        from ..core import DbItem, DrawingItem
        if self.currentIndex().isValid():
            item = self.model().itemFromIndex(self.currentIndex())
            if isinstance(item, DbItem) \
            or isinstance(item, DrawingItem):
                self.edit(self.currentIndex())

    def showContextMenu(self : 'Explorer', pos : QPoint) -> None:
        menu = QMenu(self)
        a = self.actions
        index = self.indexAt(pos)
        if not index.isValid(): # if clicking in empty space
            index = self.currentIndex()
        if index.isValid():
            new_window_action = self.actions.newItemWindow
            edit_action       = self.actions.editItem
            save_action       = self.actions.saveItem
            save_as_action    = self.actions.saveAsItem
            close_action      = self.actions.closeItem
            rename_action     = self.actions.rename
            self.item = self.model().itemFromIndex(index)
            item = self.model().itemFromIndex(index)
            match hub.model.getItemDescription(item):
                case 'Designs':
                    menu.addAction(a.newDesign)
                    menu.addAction(a.openDesign)
                case 'Libraries':
                    menu.addAction(a.newLibrary)
                    menu.addAction(a.openLibrary)
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
                    save_action.setText('Save Library')
                    save_as_action.setText('Save Library As')
                    close_action.setText('Close Library')
                    rename_action.setText('Rename Library')
                    menu.addAction(save_action)
                    menu.addAction(save_as_action)
                    menu.addAction(close_action)
                    menu.addSeparator()
                    menu.addAction(rename_action)
                case 'Diagrams':
                    menu.addAction(a.newDiagram)
                case 'Symbol Cache':
                    menu.addAction(a.newSymbol)
                case 'Diagram':
                    edit_action.setText('Edit Diagram')
                    new_window_action.setText('New Diagram Window')
                    rename_action.setText('Rename Diagram')
                    menu.addAction(edit_action)
                    menu.addAction(new_window_action)
                    menu.addSeparator()
                    menu.addAction(rename_action)
                case 'Design Symbol' | 'Library Symbol':
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

    def newDesign(self : 'Explorer') -> None:
        design_item = hub.model.newDesign()
        diagram_item = hub.model.newDiagram(design_item)
        self.expand(hub.model.indexFromItem(design_item))
        self.expand(hub.model.indexFromItem(design_item.diagrams))
        self.editItem(diagram_item)

    def newLibrary(self : 'Explorer') -> None:
        library_item = hub.model.newLibrary()
        self.expand(hub.model.indexFromItem(library_item))

    def newDiagram(self : 'Explorer', item : QStandardItem) -> None:
        diagram_item = hub.model.newDiagram(item)
        self.expand(hub.model.indexFromItem(item))
        self.editItem(diagram_item)

    def newSymbol(self : 'Explorer', item : QStandardItem) -> None:
        symbol_item = hub.model.newSymbol(item)
        self.expand(hub.model.indexFromItem(item))
        self.editItem(symbol_item)

    def open(self : 'Explorer', type_name : str) -> None:
        from .dialogs import FileOpenDialog
        dialog = FileOpenDialog(type_name)
        result = dialog.exec()
        if result == dialog.DialogCode.Accepted:
            files = dialog.selectedFiles()
            for file in files:
                hub.model.load(file)

    def editItem(self : 'Explorer', item : QStandardItem) -> None:
        from ..core    import DrawingItem
        from ..widgets import DrawingScene, DrawingView, DrawingSubWindow, \
                              SymbolScene, SymbolView, SymbolSubWindow, \
                              DiagramScene, DiagramView, DiagramSubWindow
        if isinstance(item, DrawingItem):
            # focus existing subwindow if one exists
            for subwindow in hub.main_window.mdi_area.subWindowList():
                if not isinstance(subwindow, DrawingSubWindow):
                    continue
                if not isinstance(subwindow.widget(), DrawingView):
                    continue
                if not isinstance(subwindow.widget().scene(), DrawingScene):
                    continue
                if item.scene != subwindow.widget().scene():
                    continue
                hub.main_window.mdi_area.setActiveSubWindow(subwindow)
                subwindow.show()
                subwindow.raise_()
                subwindow.setFocus()
                return
            # create new subwindow
            drawing_name = item.text()
            drawing_scene : DrawingScene = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(drawing_scene, DiagramScene):
                drawing_view = DiagramView(drawing_scene)
                db_item = item.parent().parent()
                subwindow = DiagramSubWindow(hub.main_window.mdi_area)
            elif isinstance(drawing_scene, SymbolScene):
                drawing_view = SymbolView(drawing_scene)
                db_item = item.parent()
                subwindow = SymbolSubWindow(hub.main_window.mdi_area)
            else:
                raise ValueError(f'Unknown drawing scene: {type(drawing_scene)}')
            subwindow.setWidget(drawing_view)
            subwindow.setWindowTitle(f'{db_item.text()}: {drawing_name}')
            hub.main_window.mdi_area.addSubWindow(subwindow)
            subwindow.showMaximized()
            hub.main_window.menu_bar.updateWindowMenu()
        else:
            logger.warning(f'Unsupported item: {item.text()} ({type(item)})')

    def newItemWindow(self : 'Explorer', item : 'DrawingItem') -> None:
        from ..core import DesignItem, LibraryItem, DiagramItem, SymbolItem
        from ..widgets import DiagramScene, DiagramView, DiagramSubWindow, \
                              SymbolScene, SymbolView, SymbolSubWindow
        if isinstance(item, DiagramItem):
            db_item : DesignItem = item.parent().parent()
            dwg_scene : DiagramScene = item.data(Qt.ItemDataRole.UserRole)
            dwg_view = DiagramView(dwg_scene)
            subwindow = DiagramSubWindow()
        elif isinstance(item, SymbolItem):
            db_item : LibraryItem = item.parent()
            dwg_scene : SymbolScene = item.data(Qt.ItemDataRole.UserRole)
            dwg_view = SymbolView(dwg_scene)
            subwindow = SymbolSubWindow()
        else:
            logger.warning(f'Unsupported item: {item.text()} ({type(item)})')
            return
        dwg_name = item.text()
        subwindow.setWidget(dwg_view)
        subwindow.setWindowTitle(f'{db_item.text()}:{dwg_name}')
        hub.main_window.mdi_area.addSubWindow(subwindow)
        subwindow.showMaximized()
        hub.main_window.menu_bar.updateWindowMenu()

    def saveItem(self : 'Explorer', item : 'DbItem') -> None:
        item.save()

    def saveAsItem(self : 'Explorer', item : 'DbItem') -> None:
        from .dialogs import FileSaveAsDialog
        dialog = FileSaveAsDialog(item.__class__.__name__.replace('Item', ''))
        result = dialog.exec()
        if result == dialog.DialogCode.Accepted:
            selected_files = dialog.selectedFiles()
            if len(selected_files) > 1:
                unexpected_files = [f for f in selected_files[1:]]
                logger.warning(f'Unexpected files: {unexpected_files}')
            path = selected_files[0]
            item.save(path)

    def closeItem(self : 'Explorer', item : QStandardItem) -> None:
        # TODO offer to save if modified
        hub.model.close(item)

    def copy(self : 'Explorer', item : QStandardItem) -> None:
        hub.model.copy(item)

    def paste(self : 'Explorer', item : QStandardItem) -> None:
        hub.model.paste(item)
