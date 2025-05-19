from types  import SimpleNamespace
from typing import Self, Optional

from PyQt6.QtCore    import Qt, QPoint, QItemSelectionModel
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtGui     import QAction, QStandardItem, \
                            QKeyEvent, QMouseEvent, QWheelEvent, QFocusEvent

from ...core import logger

from .tree_view import TreeView, TreeViewDock

from ... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...core import DrawingItem, DbItem


class Explorer(TreeView):
    actions   : SimpleNamespace
    menus     : SimpleNamespace
    item      : QStandardItem
    _focus_in : bool

    def __init__(self : Self, parent : QWidget) -> None:
        super().__init__(parent, hub.model)
        hub.model.itemChanged.connect(self.onItemChanged)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.setEditTriggers(self.EditTrigger.EditKeyPressed)
        self._focus_in = False
        self.actions = SimpleNamespace()
        a = self.actions
        a.increaseTextSize = QAction("Increase Text Size", self)
        a.increaseTextSize.triggered.connect(self.increaseFontSize)
        a.decreaseTextSize = QAction("Decrease Text Size", self)
        a.decreaseTextSize.triggered.connect(self.decreaseFontSize)
        a.newDesign = QAction("New Design", self)
        a.newDesign.triggered.connect(self.newDesign)
        a.newMenuDesign = QAction("Design", self)
        a.newMenuDesign.triggered.connect(self.newDesign)
        a.newLibrary = QAction("New Library", self)
        a.newLibrary.triggered.connect(self.newLibrary)
        a.newMenuLibrary = QAction("Library", self)
        a.newMenuLibrary.triggered.connect(self.newLibrary)
        a.newDiagram = QAction("New Diagram", self)
        a.newDiagram.triggered.connect(lambda: self.newDiagram(self.item))
        a.newMenuDiagram = QAction("Diagram", self)
        a.newMenuDiagram.triggered.connect(lambda: self.newDiagram(self.item))
        a.newSymbol = QAction("New Symbol", self)
        a.newSymbol.triggered.connect(lambda: self.newSymbol(self.item))
        a.newMenuSymbol = QAction("Symbol", self)
        a.newMenuSymbol.triggered.connect(lambda: self.newSymbol(self.item))
        a.open = QAction("Open...", self)
        a.open.triggered.connect(lambda: self.openDb())
        a.openDesign = QAction("Open Design...", self)
        a.openDesign.triggered.connect(lambda: self.openDb("Design"))
        a.openLibrary = QAction("Open Library...", self)
        a.openLibrary.triggered.connect(lambda: self.openDb("Library"))
        a.editDiagram = QAction("Edit Diagram", self)
        a.editDiagram.triggered.connect(lambda: self.editDrawing(self.item))
        a.editSymbol = QAction("Edit Symbol", self)
        a.editSymbol.triggered.connect(lambda: self.editDrawing(self.item))
        a.newDiagramWindow = QAction("New Diagram Window", self)
        a.newDiagramWindow.triggered.connect(lambda: self.newDrawingWindow(self.item))
        a.newSymbolWindow = QAction("New Symbol Window", self)
        a.newSymbolWindow.triggered.connect(lambda: self.newDrawingWindow(self.item))
        a.saveDesign = QAction("Save Design", self)
        a.saveDesign.triggered.connect(lambda: self.saveDb(self.item))
        a.saveLibrary = QAction("Save Library", self)
        a.saveLibrary.triggered.connect(lambda: self.saveDb(self.item))
        a.saveDesignAs = QAction("Save Design As...", self)
        a.saveDesignAs.triggered.connect(lambda: self.saveDbAs(self.item))
        a.saveLibraryAs = QAction("Save Library As...", self)
        a.saveLibraryAs.triggered.connect(lambda: self.saveDbAs(self.item))
        a.closeDesign = QAction("Close Design", self)
        a.closeDesign.triggered.connect(lambda: self.closeDb(self.item))
        a.closeLibrary = QAction("Close Library", self)
        a.closeLibrary.triggered.connect(lambda: self.closeDb(self.item))
        a.renameDesign = QAction("Rename Design", self)
        a.renameDesign.triggered.connect(self.rename)
        a.renameLibrary = QAction("Rename Library", self)
        a.renameLibrary.triggered.connect(self.rename)
        a.renameDiagram = QAction("Rename Diagram", self)
        a.renameDiagram.triggered.connect(self.rename)
        a.renameSymbol = QAction("Rename Symbol", self)
        a.renameSymbol.triggered.connect(self.rename)
        a.copy = QAction("Copy", self)
        a.copy.triggered.connect(lambda: self.copy(self.item))
        a.paste = QAction("Paste", self)
        a.paste.triggered.connect(lambda: self.paste(self.item))
        self.menus = SimpleNamespace()
        m = self.menus
        m.new_db = QMenu("New", self)
        m.new_db.addAction(a.newMenuDesign)
        m.new_db.addAction(a.newMenuLibrary)
        m.new_dwg = QMenu("New", self)
        m.new_dwg.addAction(a.newMenuDiagram)
        m.new_dwg.addAction(a.newMenuSymbol)

    def onItemChanged(self : Self, item : QStandardItem) -> None:
        """Handle changes to items in the model, such as renaming."""
        if item.parent() and item.parent().text() in ("Diagrams", "Symbol Cache"):
            scene = item.data(Qt.ItemDataRole.UserRole)
            if scene:
                scene.name = item.text()
        hub.main_window.mdi_area.update()

    def focusInEvent(self : Self, event: QFocusEvent) -> None:
        self._focus_in = True
        super().focusInEvent(event)

    def keyPressEvent(self : Self, event: QKeyEvent) -> None:
        if event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            if len(self.selectedIndexes()) == 1:
                index = self.selectedIndexes()[0]
                if index.isValid():
                    self.expandOrEdit(hub.model.itemFromIndex(index))
                    event.accept()

    def mousePressEvent(self : Self, event: QMouseEvent) -> None:
        """Handle mouse press to deselect items when clicking in empty space."""
        index = self.indexAt(event.pos())
        if not index.isValid() and event.button() in \
            [Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton]:
            if self._focus_in:
                self._focus_in = False
            else:
                self.clearSelection()
                self.setCurrentIndex(hub.model.index(-1, -1))  # invalid index
                if event.button() == Qt.MouseButton.LeftButton:
                    event.accept()
                    return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self : Self, event: QMouseEvent) -> None:
        """Handle double-click."""
        if event.button() == Qt.MouseButton.LeftButton:
            index = self.indexAt(event.pos())
            if index.isValid():
                self.expandOrEdit(hub.model.itemFromIndex(index))
                event.accept()
                return
        super().mouseDoubleClickEvent(event)

    def wheelEvent(self : Self, event: QWheelEvent) -> None:
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

    def selectItem(self : Self, item : QStandardItem) -> None:
        index = hub.model.indexFromItem(item)
        self.selectionModel().clearSelection()
        self.selectionModel().select(
            index,
            QItemSelectionModel.SelectionFlag.Select |
            QItemSelectionModel.SelectionFlag.Current
        )
        self.setCurrentIndex(index)

    def expandOrEdit(self : Self, item : QStandardItem) -> None:
        self.selectItem(item)
        match hub.model.getItemDescription(item):
            case "Designs"  | "Libraries"    | \
                 "Design"   | "Library"      | \
                 "Diagrams" | "Symbol Cache":
                index = self.currentIndex()
                self.setExpanded(index, not self.isExpanded(index))
            case "Diagram" | "Design Symbol" | "Library Symbol":
                self.editDrawing(item)

    def newDesign(self : Self) -> None:
        design_item = hub.model.newDesign()
        diagram_item = hub.model.newDiagram(design_item)
        self.expand(hub.model.indexFromItem(design_item))
        self.expand(hub.model.indexFromItem(design_item.diagrams))
        self.editDrawing(diagram_item)

    def newLibrary(self : Self) -> None:
        library_item = hub.model.newLibrary()
        self.expand(hub.model.indexFromItem(library_item))

    def newDiagram(self : Self, item : QStandardItem) -> None:
        diagram_item = hub.model.newDiagram(item)
        self.expand(hub.model.indexFromItem(item))
        self.editDrawing(diagram_item)

    def newSymbol(self : Self, item : QStandardItem) -> None:
        symbol_item = hub.model.newSymbol(item)
        self.expand(hub.model.indexFromItem(item))
        self.editDrawing(symbol_item)

    def openDb(self : Self, type_name : Optional[str] = None) -> None:
        from ..dialogs import FileOpenDialog
        dialog = FileOpenDialog(type_name)
        result = dialog.exec()
        if result == dialog.DialogCode.Accepted:
            files = dialog.selectedFiles()
            for file in files:
                hub.model.load(file)

    def editDrawing(self : Self, item : QStandardItem) -> None:
        from ...core    import DrawingItem
        from ...widgets import Drawing, DrawingView, DrawingSubWindow, \
                               Symbol, SymbolView, SymbolSubWindow, \
                               Diagram, DiagramView, DiagramSubWindow
        if isinstance(item, DrawingItem):
            # focus existing subwindow if one exists
            for subwindow in hub.main_window.mdi_area.subWindowList():
                if not isinstance(subwindow, DrawingSubWindow):
                    continue
                if not isinstance(subwindow.widget(), DrawingView):
                    continue
                if not isinstance(subwindow.widget().scene(), Drawing):
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
            drawing_scene : Drawing = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(drawing_scene, Diagram):
                drawing_view = DiagramView(drawing_scene)
                db_item = item.parent().parent()
                subwindow = DiagramSubWindow(hub.main_window.mdi_area)
            elif isinstance(drawing_scene, Symbol):
                drawing_view = SymbolView(drawing_scene)
                db_item = item.parent()
                subwindow = SymbolSubWindow(hub.main_window.mdi_area)
            else:
                raise ValueError(f"Unknown drawing scene: {type(drawing_scene)}")
            subwindow.setWidget(drawing_view)
            subwindow.setWindowTitle(f"{db_item.text()}: {drawing_name}")
            hub.main_window.mdi_area.addSubWindow(subwindow)
            subwindow.showMaximized()
            hub.main_window.menu_bar.updateWindowMenu()
        else:
            logger.warning(f"Unsupported item: {item.text()} ({type(item)})")

    def newDrawingWindow(self : Self, item : "DrawingItem") -> None:
        from ...core import DesignItem, LibraryItem, DiagramItem, SymbolItem
        from ...widgets import Diagram, DiagramView, DiagramSubWindow, \
                              Symbol, SymbolView, SymbolSubWindow
        if isinstance(item, DiagramItem):
            db_item : DesignItem = item.parent().parent()
            dwg_scene : Diagram = item.data(Qt.ItemDataRole.UserRole)
            dwg_view = DiagramView(dwg_scene)
            subwindow = DiagramSubWindow()
        elif isinstance(item, SymbolItem):
            db_item : LibraryItem = item.parent()
            dwg_scene : Symbol = item.data(Qt.ItemDataRole.UserRole)
            dwg_view = SymbolView(dwg_scene)
            subwindow = SymbolSubWindow()
        else:
            logger.warning(f"Unsupported item: {item.text()} ({type(item)})")
            return
        dwg_name = item.text()
        subwindow.setWidget(dwg_view)
        subwindow.setWindowTitle(f"{db_item.text()}:{dwg_name}")
        hub.main_window.mdi_area.addSubWindow(subwindow)
        subwindow.showMaximized()
        hub.main_window.menu_bar.updateWindowMenu()

    def saveDb(self : Self, item : "DbItem") -> None:
        item.save()

    def saveDbAs(self : Self, item : "DbItem") -> None:
        from ..dialogs import FileSaveAsDialog
        dialog = FileSaveAsDialog(item.__class__.__name__.replace("Item", ""))
        result = dialog.exec()
        if result == dialog.DialogCode.Accepted:
            selected_files = dialog.selectedFiles()
            if len(selected_files) > 1:
                unexpected_files = [f for f in selected_files[1:]]
                logger.warning(f"Unexpected files: {unexpected_files}")
            path = selected_files[0]
            item.save(path)

    def closeDb(self : Self, item : "DbItem") -> None:
        # TODO offer to save if modified
        hub.model.close(item)

    def rename(self : Self) -> None:
        """Start editing the selected item"s text."""
        from ...core import DbItem, DrawingItem
        if self.currentIndex().isValid():
            item = self.model().itemFromIndex(self.currentIndex())
            if isinstance(item, DbItem) \
            or isinstance(item, DrawingItem):
                self.edit(self.currentIndex())

    def copy(self : Self, item : QStandardItem) -> None:
        hub.model.copy(item)

    def paste(self : Self, item : QStandardItem) -> None:
        hub.model.paste(item)

    def showContextMenu(self : Self, pos : QPoint) -> None:
        menu = QMenu(self)
        a = self.actions
        m = self.menus
        index = self.indexAt(pos)
        if not index.isValid(): # if clicking in empty space
            index = self.currentIndex()
        if index.isValid():
            self.item = self.model().itemFromIndex(index)
            item = self.model().itemFromIndex(index)
            match hub.model.getItemDescription(item):
                case "Designs":
                    menu.addAction(a.newDesign)
                    menu.addAction(a.openDesign)
                case "Libraries":
                    menu.addAction(a.newLibrary)
                    menu.addAction(a.openLibrary)
                case "Design":
                    menu.addMenu(m.new_dwg)
                    menu.addAction(a.saveDesign)
                    menu.addAction(a.saveDesignAs)
                    menu.addAction(a.closeDesign)
                    menu.addSeparator()
                    menu.addAction(a.renameDesign)
                case "Library":
                    menu.addAction(a.saveLibrary)
                    menu.addAction(a.saveLibraryAs)
                    menu.addAction(a.closeLibrary)
                    menu.addSeparator()
                    menu.addAction(a.newSymbol)
                    menu.addSeparator()
                    menu.addAction(a.renameLibrary)
                case "Diagrams":
                    menu.addAction(a.newDiagram)
                case "Symbol Cache":
                    menu.addAction(a.newSymbol)
                case "Diagram":
                    menu.addAction(a.newDiagramWindow)
                    menu.addAction(a.editDiagram)
                    menu.addSeparator()
                    menu.addAction(a.renameDiagram)
                case "Design Symbol" | "Library Symbol":
                    menu.addAction(a.newSymbolWindow)
                    menu.addAction(a.editSymbol)
                    menu.addSeparator()
                    menu.addAction(a.renameSymbol)
            menu.addSeparator()
            menu.addAction(self.actions.copy)
            menu.addAction(self.actions.paste)
            menu.addSeparator()
        else:
            menu.addMenu(m.new_db)
            menu.addAction(a.open)
            menu.addSeparator()
        menu.addAction(self.actions.increaseTextSize)
        menu.addAction(self.actions.decreaseTextSize)
        menu.exec(self.viewport().mapToGlobal(pos))

class ExplorerDock(TreeViewDock):
    WINDOW_TITLE = "Explorer"

    explorer : Explorer

    def __init__(self : Self, parent : QWidget) -> None:
        super().__init__(parent, None)
        self.explorer = Explorer(self)
        self.setWidget(self.explorer)
