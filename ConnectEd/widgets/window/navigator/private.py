from PyQt6.QtCore import QItemSelectionModel

from ....app import logger, settings, model, window

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....core.db import Node, DbNode, DbNodeType, \
                            DrawingNode, DrawingWindowNode, \
                            SpreadsheetWindowNode
    from . import Navigator


class NavigatorPrivateMixin:

    def _nodeTypeOK(self : "Navigator", node : "Node", type_ : type) -> None:
        if not isinstance(node, type_):
            logger().warning(
                f"Unsupported node: {self.node.text()} ({type(self.node)})"
            )
            return False
        return True

    def _selectItem(self : "Navigator", node : "Node") -> None:
        index = model().indexFromItem(node)
        self.selectionModel().clearSelection()
        self.selectionModel().select(
            index,
            QItemSelectionModel.SelectionFlag.Select |
            QItemSelectionModel.SelectionFlag.Current
        )
        self.setCurrentIndex(index)

    def _expandDb(self : "Navigator", node : "DbNode") -> None:
        from ....core.db import DesignDbNode, LibraryDbNode
        db_idx = model().indexFromItem(node)
        self.expand(db_idx)
        if isinstance(node, DesignDbNode):
            diagrams_idx = model().indexFromItem(node._diagrams)
            self.expand(diagrams_idx)
        elif isinstance(node, LibraryDbNode):
            symbols_idx = model().indexFromItem(node._symbols)
            self.expand(symbols_idx)

    def _expandOrEdit(self : "Navigator", node : "Node") -> None:
        self._selectItem(node)
        match model().getNodeDescription(node):
            case "Designs"  | "Libraries"    | \
                 "Design"   | "Library"      | \
                 "Diagrams" | "Symbol Cache":
                index = self.currentIndex()
                self.setExpanded(index, not self.isExpanded(index))
            case "Diagram" | "Design Symbol" | "Library Symbol":
                self._editDrawing(node)

    def _openDb(self : "Navigator", type_name : str | None = None) -> None:
        from ...dialogs.file import FileOpenDialog
        dialog = FileOpenDialog(type_name)
        result = dialog.exec()
        if result == dialog.DialogCode.Accepted:
            files = dialog.selectedFiles()
            for file in files:
                if self._openDbFile(file):
                    settings().addMRU(file)

    def _openDbFile(self : "Navigator", file_name : str) -> "DbNodeType | None":
        db_node = model().load(file_name)
        if db_node:
            self._expandDb(db_node)
            if hasattr(db_node, "rootDiagramNode"):
                self._editDrawing(db_node.rootDiagramNode())
        return db_node

    def _editDrawing(self : "Navigator", node : "DrawingNode") -> None:
        from ....core.db import DrawingNode, DrawingWindowNode
        if not self._nodeTypeOK(node, DrawingNode):
            return
        # open first existing window if one exists
        for row in range(node.rowCount()):
            child = node.child(row)
            if isinstance(child, DrawingWindowNode):
                self._activateDrawingWindow(child)
                return
        # otherwise create a new window
        self._newDrawingWindow(node)

    def _newDrawingWindow(self : "Navigator", node : "DrawingNode") -> None:
        from ....core.db import DesignDbNode, LibraryDbNode, \
                               DiagramNode, SymbolNode
        from ....widgets.graphics.views.diagram  import DiagramView, DiagramSubWindow
        from ....widgets.graphics.views.symbol   import SymbolView, SymbolSubWindow
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

    def _activateDrawingWindow(self : "Navigator", node : "DrawingWindowNode") -> None:
        from ....core.db import DrawingWindowNode
        if not isinstance(node, DrawingWindowNode):
            logger().warning(f"Unsupported node: {node.text()} ({type(node)})")
            return
        subwindow = node.subwindow()
        subwindow.show()
        subwindow.raise_()
        subwindow.setFocus()

    def _spreadsheet(self : "Navigator", node : "DrawingNode") -> None:
        from ....core.db import DrawingNode
        from ..spreadsheet import SpreadsheetSubWindow
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

    def _save(self : "Navigator", node : "DbNode") -> None:
        # TODO handle overwrite
        node.save()

    def _saveAs(self : "Navigator", node : "DbNode") -> None:
        from ...dialogs.file import FileSaveAsDialog
        dialog = FileSaveAsDialog(node.dbTypeName())
        result = dialog.exec()
        if result == dialog.DialogCode.Accepted:
            selected_files = dialog.selectedFiles()
            if len(selected_files) > 1:
                unexpected_files = [f for f in selected_files[1:]]
                logger().warning(f"Unexpected files: {unexpected_files}")
            path = selected_files[0]
            node.save(path)

    def _close(self : "Navigator", node : "DbNode") -> None:
        # TODO offer to save if modified
        model().close(node)

    def _updateWindowTitles(self : "Navigator", node : "DrawingNode") -> None:
        from ....core.db import DrawingWindowNode, SpreadsheetWindowNode
        if node.rowCount() == 0:
            return
        drawing_window_nodes : list[DrawingWindowNode] = []
        spreadsheet_window_nodes : list[SpreadsheetWindowNode] = []
        for row in range(node.rowCount()):
            child = node.child(row)
            if isinstance(child, DrawingWindowNode):
                drawing_window_nodes.append(child)
            elif isinstance(child, SpreadsheetWindowNode):
                spreadsheet_window_nodes.append(child)
        title = f"{node.dbNode().text()}:{node.text()}"
        for i, dn in enumerate(drawing_window_nodes):
            suffix = f" ({i + 1})" if len(drawing_window_nodes) > 1 else ""
            dn.setText("Drawing Editor" + suffix)
            dn.setWindowTitle(title + " - Drawing Editor" + suffix)
        for i, sn in enumerate(spreadsheet_window_nodes):
            suffix = f" ({i + 1})" if len(spreadsheet_window_nodes) > 1 else ""
            sn.setText("Properties Editor" + suffix)
            sn.setWindowTitle(title + " - Properties Editor" + suffix)
