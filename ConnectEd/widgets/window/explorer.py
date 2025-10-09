from types  import SimpleNamespace
from typing import Self

from PyQt6.QtCore    import Qt, QPoint, QItemSelectionModel
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui     import QKeyEvent, QMouseEvent, QWheelEvent, QFocusEvent, \
                            QAction

from ...app import logger, settings, model, window

from ...widgets.graphics.items.anchor_point import AnchorPoint
from ...widgets.graphics.items.tether_text  import Tether

from ..menu import Menu

from .tree_view import TreeView, TreeViewDock

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...core.db import Node, DrawingNode, DbNode


class Explorer(TreeView):
    actions   : SimpleNamespace
    menus     : SimpleNamespace
    node      : "Node"
    _focus_in : bool

    def __init__(self : Self, parent : QWidget) -> None:
        super().__init__(model(), parent)
        model().itemChanged.connect(self.onItemChanged)
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
        a.newDiagram.triggered.connect(lambda: self.newDiagram(self.node))
        a.newMenuDiagram = QAction("Diagram", self)
        a.newMenuDiagram.triggered.connect(lambda: self.newDiagram(self.node))
        a.newSymbol = QAction("New Symbol", self)
        a.newSymbol.triggered.connect(lambda: self.newSymbol(self.node))
        a.newMenuSymbol = QAction("Symbol", self)
        a.newMenuSymbol.triggered.connect(lambda: self.newSymbol(self.node))
        a.open = QAction("Open...", self)
        a.open.triggered.connect(lambda: self.openDbFiles())
        a.openDesign = QAction("Open Design...", self)
        a.openDesign.triggered.connect(lambda: self.openDbFiles("Design"))
        a.openLibrary = QAction("Open Library...", self)
        a.openLibrary.triggered.connect(lambda: self.openDbFiles("Library"))
        a.editDiagram = QAction("Edit Diagram", self)
        a.editDiagram.triggered.connect(lambda: self.editDrawing(self.node))
        a.editSymbol = QAction("Edit Symbol", self)
        a.editSymbol.triggered.connect(lambda: self.editDrawing(self.node))
        a.newDiagramWindow = QAction("New Diagram Window", self)
        a.newDiagramWindow.triggered.connect(lambda: self.newDrawingWindow(self.node))
        a.newSymbolWindow = QAction("New Symbol Window", self)
        a.newSymbolWindow.triggered.connect(lambda: self.newDrawingWindow(self.node))
        a.spreadsheet = QAction("Spreadsheet", self)
        a.spreadsheet.triggered.connect(lambda: self.spreadsheet(self.node))
        a.saveDesign = QAction("Save Design", self)
        a.saveDesign.triggered.connect(lambda: self.saveDb(self.node))
        a.saveLibrary = QAction("Save Library", self)
        a.saveLibrary.triggered.connect(lambda: self.saveDb(self.node))
        a.saveDesignAs = QAction("Save Design As...", self)
        a.saveDesignAs.triggered.connect(lambda: self.saveDbAs(self.node))
        a.saveLibraryAs = QAction("Save Library As...", self)
        a.saveLibraryAs.triggered.connect(lambda: self.saveDbAs(self.node))
        a.closeDesign = QAction("Close Design", self)
        a.closeDesign.triggered.connect(lambda: self.closeDb(self.node))
        a.closeLibrary = QAction("Close Library", self)
        a.closeLibrary.triggered.connect(lambda: self.closeDb(self.node))
        a.renameDesign = QAction("Rename Design", self)
        a.renameDesign.triggered.connect(self.rename)
        a.renameLibrary = QAction("Rename Library", self)
        a.renameLibrary.triggered.connect(self.rename)
        a.renameDiagram = QAction("Rename Diagram", self)
        a.renameDiagram.triggered.connect(self.rename)
        a.renameSymbol = QAction("Rename Symbol", self)
        a.renameSymbol.triggered.connect(self.rename)
        a.copy = QAction("Copy", self)
        a.copy.triggered.connect(lambda: self.copy(self.node))
        a.paste = QAction("Paste", self)
        a.paste.triggered.connect(lambda: self.paste(self.node))
        self.menus = SimpleNamespace()
        m = self.menus
        m.new_db = Menu("New", self)
        m.new_db.addAction(a.newMenuDesign)
        m.new_db.addAction(a.newMenuLibrary)
        m.new_dwg = Menu("New", self)
        m.new_dwg.addAction(a.newMenuDiagram)
        m.new_dwg.addAction(a.newMenuSymbol)

    def onItemChanged(self : Self, item : "Node") -> None:
        """Handle changes to items in the model, such as renaming."""
        scene = item.scene() if hasattr(item, "scene") else None
        if scene:
            scene.setName(item.text())
        window().mdi_area.update()

    def focusInEvent(self : Self, event : QFocusEvent) -> None:
        self._focus_in = True
        super().focusInEvent(event)

    def keyPressEvent(self : Self, event : QKeyEvent) -> None:
        if event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            if len(self.selectedIndexes()) == 1:
                index = self.selectedIndexes()[0]
                if index.isValid():
                    self.expandOrEdit(model().itemFromIndex(index))
                    event.accept()

    def mousePressEvent(self : Self, event : QMouseEvent) -> None:
        """Handle mouse press to deselect items when clicking in empty space."""
        index = self.indexAt(event.pos())
        if not index.isValid() and event.button() in \
            [Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton]:
            if self._focus_in:
                self._focus_in = False
            else:
                self.clearSelection()
                self.setCurrentIndex(model().index(-1, -1))  # invalid index
                if event.button() == Qt.MouseButton.LeftButton:
                    event.accept()
                    return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self : Self, event : QMouseEvent) -> None:
        """Handle double-click."""
        if event.button() == Qt.MouseButton.LeftButton:
            index = self.indexAt(event.pos())
            if index.isValid():
                self.expandOrEdit(model().itemFromIndex(index))
                event.accept()
                return
        super().mouseDoubleClickEvent(event)

    def wheelEvent(self : Self, event : QWheelEvent) -> None:
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

    def selectItem(self : Self, item : "Node") -> None:
        index = model().indexFromItem(item)
        self.selectionModel().clearSelection()
        self.selectionModel().select(
            index,
            QItemSelectionModel.SelectionFlag.Select |
            QItemSelectionModel.SelectionFlag.Current
        )
        self.setCurrentIndex(index)

    def expandOrEdit(self : Self, item : "Node") -> None:
        self.selectItem(item)
        match model().getNodeDescription(item):
            case "Designs"  | "Libraries"    | \
                 "Design"   | "Library"      | \
                 "Diagrams" | "Symbol Cache":
                index = self.currentIndex()
                self.setExpanded(index, not self.isExpanded(index))
            case "Diagram" | "Design Symbol" | "Library Symbol":
                self.editDrawing(item)

    def newDesign(self : Self) -> None:
        # create new design
        design_db_node = model().newDesignDbNode()
        # create new diagram
        diagram_node = design_db_node.newDiagramNode()
        # expand design to show diagram and symbol cache containers
        self.expand(model().indexFromItem(design_db_node))
        # expand diagrams container to show new diagram
        self.expand(model().indexFromItem(design_db_node.diagramsNode()))
        # open diagram editor for new diagram
        self.editDrawing(diagram_node)

    def newLibrary(self : Self) -> None:
        library_item = model().newLibraryDbNode()
        self.expand(model().indexFromItem(library_item))

    def newDiagram(self : Self, item : "Node") -> None:
        diagram_node = model().newDiagramNode(item)
        self.expand(model().indexFromItem(item))
        self.editDrawing(diagram_node)

    def newSymbol(self : Self, item : "Node") -> None:
        symbol_node = model().newSymbolNode(item)
        self.expand(model().indexFromItem(item))
        self.editDrawing(symbol_node)

    def openDbFiles(self : Self, type_name : str | None = None) -> None:
        from ..dialogs.file import FileOpenDialog
        dialog = FileOpenDialog(type_name)
        result = dialog.exec()
        if result == dialog.DialogCode.Accepted:
            files = dialog.selectedFiles()
            for file in files:
                if self.openDbFile(file):
                    settings().addMRU(file)

    def openDbFile(self : Self, file_name : str) -> "DbNode | None":
        db_item = model().load(file_name)
        if db_item:
            self._expandDb(db_item)
            if hasattr(db_item, "rootDiagramNode"):
                self.editDrawing(db_item.rootDiagramNode())
        return db_item

    def editDrawing(self : Self, item : "Node") -> None:
        from ...core.db import DrawingNode
        from ...widgets.graphics.views.drawing import DrawingView, DrawingSubWindow
        from ...widgets.graphics.scenes.drawing import DrawingScene
        if isinstance(item, DrawingNode):
            # focus existing subwindow if one exists
            for subwindow in window().mdi_area.subWindowList():
                if not isinstance(subwindow, DrawingSubWindow):
                    continue
                if not isinstance(subwindow.widget(), DrawingView):
                    continue
                if not isinstance(subwindow.widget().scene(), DrawingScene):
                    continue
                if item._scene != subwindow.widget().scene():
                    continue
                window().mdi_area.setActiveSubWindow(subwindow)
                subwindow.show()
                subwindow.raise_()
                subwindow.setFocus()
                return
            self.newDrawingWindow(item)
        else:
            logger().warning(f"Unsupported item: {item.text()} ({type(item)})")

    def newDrawingWindow(self : Self, item : "DrawingNode") -> None:
        from ...core.db import DesignDbNode, LibraryDbNode, \
                               DiagramNode, SymbolNode
        from ...widgets.graphics.views.diagram  import DiagramView, DiagramSubWindow
        from ...widgets.graphics.views.symbol   import SymbolView, SymbolSubWindow
        if isinstance(item, DiagramNode):
            db_item : DesignDbNode = item.parent().parent()
            dwg_scene = item.scene()
            dwg_view = DiagramView(dwg_scene)
            subwindow = DiagramSubWindow(window().mdi_area)
        elif isinstance(item, SymbolNode):
            db_item : LibraryDbNode = item.parent()
            dwg_scene = item.scene()
            dwg_view = SymbolView(dwg_scene)
            subwindow = SymbolSubWindow(window().mdi_area)
        else:
            logger().warning(f"Unsupported item: {item.text()} ({type(item)})")
            return
        dwg_name = item.text()
        subwindow.setWidget(dwg_view)
        subwindow.setWindowTitle(f"{db_item.text()}:{dwg_name}")
        window().mdi_area.addSubWindow(subwindow)
        subwindow.showMaximized()
        window().menu_bar.updateWindowMenu()

    def spreadsheet(self : Self, item : "DrawingNode") -> None:
        from ...core.db import DrawingNode
        from .spreadsheet import SpreadsheetSubWindow
        if not isinstance(item, DrawingNode):
            logger().warning(f"Unsupported item: {item.text()} ({type(item)})")
            return
        scene = item.scene()
        for subwindow in window().mdi_area.subWindowList():
            if isinstance(subwindow, SpreadsheetSubWindow) and subwindow.scene() == scene:
                window().mdi_area.setActiveSubWindow(subwindow)
                subwindow.show()
                subwindow.raise_()
                subwindow.setFocus()
                return
        db_item = item.parent().parent()
        elements = [e for e in scene.items() \
                    if not isinstance(e, AnchorPoint | Tether)]
        subwindow = SpreadsheetSubWindow(scene, elements)
        subwindow.setWindowTitle(f"{db_item.text()}:{item.text()}: Properties")
        window().mdi_area.addSubWindow(subwindow)
        subwindow.showMaximized()
        window().menu_bar.updateWindowMenu()

    def saveDb(self : Self, item : "DbNode") -> None:
        item.save()

    def saveDbAs(self : Self, item : "DbNode") -> None:
        from ..dialogs.file import FileSaveAsDialog
        dialog = FileSaveAsDialog(item.dbTypeName())
        result = dialog.exec()
        if result == dialog.DialogCode.Accepted:
            selected_files = dialog.selectedFiles()
            if len(selected_files) > 1:
                unexpected_files = [f for f in selected_files[1:]]
                logger().warning(f"Unexpected files: {unexpected_files}")
            path = selected_files[0]
            item.save(path)

    def closeDb(self : Self, item : "DbNode") -> None:
        # TODO offer to save if modified
        model().close(item)

    def rename(self : Self) -> None:
        """Start editing the selected item"s text."""
        from ...core.db import DbNode, DrawingNode
        if self.currentIndex().isValid():
            item = model().itemFromIndex(self.currentIndex())
            if isinstance(item, DbNode) \
            or isinstance(item, DrawingNode):
                self.edit(self.currentIndex())

    def copy(self : Self, item : "Node") -> None:
        model().copy(item)

    def paste(self : Self, item : "Node") -> None:
        model().paste(item)

    def showContextMenu(self : Self, pos : QPoint) -> None:
        menu = Menu(self)
        a = self.actions
        m = self.menus
        index = self.indexAt(pos)
        if not index.isValid(): # if clicking in empty space
            index = self.currentIndex()
        if index.isValid():
            self.node = model().itemFromIndex(index)
            item = model().itemFromIndex(index)
            match model().getNodeDescription(item):
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
                    menu.addAction(a.renameDiagram)
                    menu.addSeparator()
                    menu.addAction(a.spreadsheet)
                case "Design Symbol" | "Library Symbol":
                    menu.addAction(a.newSymbolWindow)
                    menu.addAction(a.editSymbol)
                    menu.addAction(a.renameSymbol)
                    menu.addSeparator()
                    menu.addAction(a.spreadsheet)
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

    def _expandDb(self : Self, item : "DbNode") -> None:
        from ...core.db import DesignDbNode, LibraryDbNode
        db_idx = model().indexFromItem(item)
        self.expand(db_idx)
        if isinstance(item, DesignDbNode):
            diagrams_idx = model().indexFromItem(item._diagrams)
            self.expand(diagrams_idx)
        elif isinstance(item, LibraryDbNode):
            symbols_idx = model().indexFromItem(item._symbols)
            self.expand(symbols_idx)

class ExplorerDock(TreeViewDock):
    WINDOW_TITLE = "Explorer"

    explorer : Explorer

    def __init__(self : Self, parent : QWidget) -> None:
        super().__init__(None, parent)
        self.explorer = Explorer(self)
        self.setWidget(self.explorer)
