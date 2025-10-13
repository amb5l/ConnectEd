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
    from ...core.db import Node, \
                           DesignsDbContainer, LibrariesDbContainer, \
                           DesignDbNode, LibraryDbNode, \
                           DrawingWindowNode, \
                           DrawingNode, DiagramNode, SymbolNode, \
                           DbNode, DbNodeType


_MENU_SPECS = (
    ("DesignsDbContainer", (
        ( "New Design"  , "newDesign"  ),
        ( "Open Design" , "openDesign" )
    )),
    ("LibrariesDbContainer", (
        ( "New Library"  , "newLibrary"  ),
        ( "Open Library" , "openLibrary" )
    )),
    ("DesignDbNode", (
        ("New", (
            ( "Diagram" , "newDiagram" ),
            ( "Symbol"  , "newSymbol"  )
        )),
        ( "Save"    , "saveDesign"   ),
        ( "Save As" , "saveDesignAs" ),
        ( "Close"   , "closeDesign"  ),
        "--",
        ( "Rename"  , "renameDesign" )
    )),
    ("LibraryDbNode", (
        ( "New Symbol" , "newSymbol" ),
        "--",
        ( "Save"    , "saveLibrary"  ),
        ( "Save As" , "saveLibraryAs" ),
        ( "Close"   , "closeLibrary"  ),
        "--",
        ( "Rename"  , "renameLibrary" )
    )),
    ("DiagramsContainer", (
        ( "New Diagram" , "newDiagram" ),
    )),
    ("SymbolCacheContainer", (
        ( "New Symbol" , "newSymbol" ),
    )),
    ("DiagramNode", (
        ( "Edit"       , "editDiagram"      ),
        ( "Rename"     , "renameDiagram"    ),
        ( "New Window" , "newDiagramWindow" ),
        "--",
        ( "Spreadsheet" , "spreadsheet" )
    )),
    ("SymbolNode", (
        ( "Edit"       , "editSymbol"      ),
        ( "Rename"     , "renameSymbol"    ),
        ( "New Window" , "newSymbolWindow" )
    )),
    ("DrawingWindowNode", (
        ( "Activate"   , "activateDrawingWindow" ),
        ( "New Window" , "newDrawingWindow"      ),
    )),
    ("SymbolWindowNode", (
        ( "Activate"   , "activateDrawingWindow" ),
        ( "New Window" , "newSymbolWindow"       )
    ))
)


class Navigator(TreeView):

    menus     : dict[str, Menu]
    node      : "Node"
    _focus_in : bool

    def __init__(self : Self, parent : QWidget) -> None:
        super().__init__(model(), parent)
        model().itemChanged.connect(self.onItemChanged)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.setEditTriggers(self.EditTrigger.EditKeyPressed)
        self._focus_in = False
        self.menus = {}
        self._buildMenus(_MENU_SPECS)

    def onItemChanged(self : Self, node : "Node") -> None:
        """Handle changes to items in the model, such as renaming."""
        scene = node.scene() if hasattr(node, "scene") else None
        if scene:
            scene.setName(node.text())
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

    def selectItem(self : Self, node : "Node") -> None:
        index = model().indexFromItem(node)
        self.selectionModel().clearSelection()
        self.selectionModel().select(
            index,
            QItemSelectionModel.SelectionFlag.Select |
            QItemSelectionModel.SelectionFlag.Current
        )
        self.setCurrentIndex(index)

    def expandOrEdit(self : Self, node : "Node") -> None:
        self.selectItem(node)
        match model().getNodeDescription(node):
            case "Designs"  | "Libraries"    | \
                 "Design"   | "Library"      | \
                 "Diagrams" | "Symbol Cache":
                index = self.currentIndex()
                self.setExpanded(index, not self.isExpanded(index))
            case "Diagram" | "Design Symbol" | "Library Symbol":
                self.editDrawing(node)

    def newDesign(self : Self, _node : "DesignsDbContainer | None" = None) -> None:
        # create new design
        design_db_node = model().newDesignDbNode()
        # create new diagram inside design
        diagram_node = design_db_node.newDiagramNode()
        # expand design to show diagrams and symbols containers
        self.expand(model().indexFromItem(design_db_node))
        # expand diagrams container to show new diagram
        self.expand(model().indexFromItem(design_db_node.diagramsNode()))
        # open diagram editor for new diagram
        self.editDrawing(diagram_node)

    def openDesign(self : Self) -> None:
        self.openDbFiles("Design")

    def saveDesign(self : Self) -> None:
        self.saveDb(self.node)

    def saveDesignAs(self : Self) -> None:
        self.saveDbAs(self.node)

    def renameDesign(self : Self) -> None:
        self.rename(self.node)

    def closeDesign(self : Self, node : "DesignDbNode") -> None:
        self.closeDb(node)

    def newLibrary(self : Self, _node : "LibrariesDbContainer | None" = None) -> None:
        library_db_node = model().newLibraryDbNode()
        self.expand(model().indexFromItem(library_db_node))

    def openLibrary(self : Self) -> None:
        self.openDbFiles("Library")

    def saveLibrary(self : Self) -> None:
        self.saveDb(self.node)

    def saveLibraryAs(self : Self) -> None:
        self.saveDbAs(self.node)

    def renameLibrary(self : Self) -> None:
        self.rename(self.node)

    def closeLibrary(self : Self) -> None:
        self.closeDb(self.node)

    def renameDesign(self : Self) -> None:
        self.renameDb(self.node)

    def newDiagram(self : Self, node : "Node") -> None:
        diagram_node = model().newDiagramNode(node)
        self.expand(model().indexFromItem(node))
        self.editDrawing(diagram_node)

    def editDiagram(self : Self, node : "DiagramNode") -> None:
        self.editDrawing(node)

    def renameDiagram(self : Self, node : "DiagramNode") -> None:
        self.rename(node)

    def newDiagramWindow(self : Self, node : "DiagramNode") -> None:
        node.newDiagramWindow()

    def newSymbol(self : Self, node : "Node") -> None:
        symbol_node = model().newSymbolNode(node)
        self.expand(model().indexFromItem(node))
        self.editDrawing(symbol_node)

    def editSymbol(self : Self, node : "SymbolNode") -> None:
        self.editDrawing(node)

    def renameSymbol(self : Self, node : "SymbolNode") -> None:
        self.rename(node)

    def newSymbolWindow(self : Self, node : "SymbolNode") -> None:
        self.newDrawingWindow(node)

    def openDbFiles(self : Self, type_name : str | None = None) -> None:
        from ..dialogs.file import FileOpenDialog
        dialog = FileOpenDialog(type_name)
        result = dialog.exec()
        if result == dialog.DialogCode.Accepted:
            files = dialog.selectedFiles()
            for file in files:
                if self.openDbFile(file):
                    settings().addMRU(file)

    def openDbFile(self : Self, file_name : str) -> "DbNodeType | None":
        db_node = model().load(file_name)
        if db_node:
            self._expandDb(db_node)
            if hasattr(db_node, "rootDiagramNode"):
                self.editDrawing(db_node.rootDiagramNode())
        return db_node

    def editDrawing(self : Self, node : "DrawingNode") -> None:
        from ...core.db import DrawingWindowNode, DrawingNode
        if not isinstance(node, DrawingNode):
            logger().warning(f"Unsupported node: {node.text()} ({type(node)})")
            return
        # open first existing window if one exists
        for row in range(node.rowCount()):
            child = node.child(row)
            if isinstance(child, DrawingWindowNode):
                self.activateDrawingWindow(child)
                return
        # otherwise create a new window
        self.newDrawingWindow(node)

    def newDrawingWindow(self : Self, node : "DrawingNode") -> None:
        from ...core.db import DesignDbNode, LibraryDbNode, \
                               DiagramNode, SymbolNode
        from ...widgets.graphics.views.diagram  import DiagramView, DiagramSubWindow
        from ...widgets.graphics.views.symbol   import SymbolView, SymbolSubWindow
        if isinstance(node, DiagramNode):
            node.newDiagramWindow()
            db_node : DesignDbNode = node.parent().parent()
            dwg_scene = node.scene()
            dwg_view = DiagramView(dwg_scene)
            subwindow = DiagramSubWindow(window().mdi_area)
        elif isinstance(node, SymbolNode):
            db_node : LibraryDbNode = node.parent()
            dwg_scene = node.scene()
            dwg_view = SymbolView(dwg_scene)
            subwindow = SymbolSubWindow(window().mdi_area)
        else:
            logger().warning(f"Unsupported node: {node.text()} ({type(node)})")
            return
        dwg_name = node.text()
        subwindow.setWidget(dwg_view)
        subwindow.setWindowTitle(f"{db_node.text()}:{dwg_name}")
        window().mdi_area.addSubWindow(subwindow)
        subwindow.showMaximized()
        window().menu_bar.updateWindowMenu()

    def activateDrawingWindow(self : Self, node : "DrawingWindowNode") -> None:
        from ...core.db import DrawingWindowNode
        if not isinstance(node, DrawingWindowNode):
            logger().warning(f"Unsupported node: {node.text()} ({type(node)})")
            return
        subwindow = node.subwindow()
        subwindow.show()
        subwindow.raise_()
        subwindow.setFocus()

    def spreadsheet(self : Self, node : "DrawingNode") -> None:
        from ...core.db import DrawingNode
        from .spreadsheet import SpreadsheetSubWindow
        if not isinstance(node, DrawingNode):
            logger().warning(f"Unsupported node: {node.text()} ({type(node)})")
            return
        scene = node.scene()
        for subwindow in window().mdi_area.subWindowList():
            if isinstance(subwindow, SpreadsheetSubWindow) and subwindow.scene() == scene:
                window().mdi_area.setActiveSubWindow(subwindow)
                subwindow.show()
                subwindow.raise_()
                subwindow.setFocus()
                return
        db_node = node.parent().parent()
        elements = [e for e in scene.items() \
                    if not isinstance(e, AnchorPoint | Tether)]
        subwindow = SpreadsheetSubWindow(scene, elements)
        subwindow.setWindowTitle(f"{db_node.text()}:{node.text()}: Properties")
        window().mdi_area.addSubWindow(subwindow)
        subwindow.showMaximized()
        window().menu_bar.updateWindowMenu()

    def saveDb(self : Self, node : "DbNode") -> None:
        node.save()

    def saveDbAs(self : Self, node : "DbNode") -> None:
        from ..dialogs.file import FileSaveAsDialog
        dialog = FileSaveAsDialog(node.dbTypeName())
        result = dialog.exec()
        if result == dialog.DialogCode.Accepted:
            selected_files = dialog.selectedFiles()
            if len(selected_files) > 1:
                unexpected_files = [f for f in selected_files[1:]]
                logger().warning(f"Unexpected files: {unexpected_files}")
            path = selected_files[0]
            node.save(path)

    def closeDb(self : Self, node : "DbNode") -> None:
        # TODO offer to save if modified
        model().close(node)

    def rename(self : Self) -> None:
        """Start editing the selected node's text."""
        from ...core.db import DbNode, DrawingNode
        if self.currentIndex().isValid():
            node = model().itemFromIndex(self.currentIndex())
            if isinstance(node, DbNode) \
            or isinstance(node, DrawingNode):
                self.edit(self.currentIndex())

    def copy(self : Self, node : "Node") -> None:
        model().copy(node)

    def paste(self : Self, node : "Node") -> None:
        model().paste(node)

    def showContextMenu(self : Self, pos : QPoint) -> None:
        index = self.indexAt(pos)
        if not index.isValid(): # if clicking in empty space
            index = self.currentIndex()
        if index.isValid():
            self.node = model().itemFromIndex(index)
            node_type_name = type(self.node).__name__
            if node_type_name not in self.menus:
                logger().error(f"Unknown node type: {node_type_name}")
                return
            menu = self.menus[node_type_name]
            menu.exec(self.viewport().mapToGlobal(pos))

    def _expandDb(self : Self, node : "DbNode") -> None:
        from ...core.db import DesignDbNode, LibraryDbNode
        db_idx = model().indexFromItem(node)
        self.expand(db_idx)
        if isinstance(node, DesignDbNode):
            diagrams_idx = model().indexFromItem(node._diagrams)
            self.expand(diagrams_idx)
        elif isinstance(node, LibraryDbNode):
            symbols_idx = model().indexFromItem(node._symbols)
            self.expand(symbols_idx)

    def _buildMenus(
        self  : Self,
        specs : tuple[tuple]
    ) -> None:
        for name, spec in specs:
            self.menus[name] = self._buildMenu(spec)

    def _buildMenu(
        self : Self,
        spec : tuple[str, str | tuple]
    ) -> Menu:
        # create empty menu
        menu = Menu(self)
        # add actions/submenus to menu
        for name, method_or_spec in spec:
            if isinstance(method_or_spec, str):  # it's a method name
                if method_or_spec.startswith("-"):
                    action = QAction()
                    action.setSeparator(True)
                    menu.addSeparator()
                else:
                    action = QAction(name, self)
                    method = getattr(self, method_or_spec)
                    wrapper = lambda checked=False, m=method: m(self.node)
                    action.triggered.connect(wrapper)
                menu.addAction(action)
            elif isinstance(method_or_spec, tuple):  # it's a submenu spec
                # this entry is a submenu
                submenu = self._buildMenu(method_or_spec)
                menu.addMenu(submenu)
            else:
                logger().error(f"Unknown entry type: {method_or_spec}")
                continue
        return menu


class NavigatorDock(TreeViewDock):
    WINDOW_TITLE = "Navigator"

    navigator : Navigator

    def __init__(self : Self, parent : QWidget) -> None:
        super().__init__(None, parent)
        self.navigator = Navigator(self)
        self.setWidget(self.navigator)
