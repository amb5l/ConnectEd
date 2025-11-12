from PyQt6.QtCore import QItemSelectionModel

from ....app import logger, settings, model, window

from ....core.utils import typeCheck

from ....widgets.graphics.items.handle        import Handle
from ....widgets.graphics.items.property_text import Tether

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....core.db import Node, DrawingNode, SymbolNode, \
                            DbNode, DesignDbNode, LibraryDbNode
    from . import Navigator


class NavigatorPrivateMixin:

    def _selectItem(self : "Navigator", node : "Node") -> None:
        index = model().indexFromItem(node)
        self.selectionModel().clearSelection()
        self.selectionModel().select(
            index,
            QItemSelectionModel.SelectionFlag.Select |
            QItemSelectionModel.SelectionFlag.Current
        )
        self.setCurrentIndex(index)

    def _doubleClickOrEnter(
        self : "Navigator",
        node : "DesignDbNode | LibraryDbNode | SymbolNode"
    ) -> None:
        from ....core.db import DesignDbNode, LibraryDbNode, SymbolNode
        if not isinstance(node, DesignDbNode | LibraryDbNode | SymbolNode):
            logger().warning(f"Unsupported node: {node.text()} ({type(node)})")
            return
        self._selectItem(node)
        if isinstance(node, DesignDbNode | SymbolNode):
            self._editDrawing(node)
        elif isinstance(node, LibraryDbNode):
            index = self.currentIndex()
            self.setExpanded(index, not self.isExpanded(index))

    def _open(self : "Navigator", type_name : str | None = None) -> None:
        from ...dialogs.file import FileOpenDialog
        dialog = FileOpenDialog(type_name)
        result = dialog.exec()
        if result == dialog.DialogCode.Accepted:
            files = dialog.selectedFiles()
            for file in files:
                if self._load(file):
                    settings().addMRU(file)

    def _load(
        self : "Navigator",
        path : str
    ) -> "DesignDbNode | LibraryDbNode | None":
        """
        Load diagram or library from file. Expand. Open drawing if diagram.
        """
        from ....core.db import DesignDbNode, LibraryDbNode
        db_node = model().load(path)
        if not isinstance(db_node, DesignDbNode | LibraryDbNode):
            logger().warning(f"Load failed ({type(db_node)})")
            return None
        self.expand(model().indexFromItem(db_node))
        if isinstance(db_node, DesignDbNode):
            self._editDrawing(db_node)
        return db_node

    def _editDrawing(self : "Navigator", node : "DesignDbNode | DrawingNode") -> None:
        """
        Either bring existing window to front or create a new one.
        """
        from ....core.db import DesignDbNode, DrawingNode
        if not typeCheck(node, DesignDbNode | DrawingNode):
            return
        scene = node.scene()
        # get existing subwindows in top down Z order
        subwindows = window().mdi_area.sceneSubWindows(scene)
        if subwindows:
            # bring existing window to front
            window().mdi_area.activateSubWindow(subwindows[0])
        else:
            # create a new window
            self._newDrawingWindow(node)

    def _newDrawingWindow(
        self : "Navigator",
        node : "DesignDbNode | SymbolNode"
    ) -> None:
        from ....core.db import DesignDbNode, SymbolNode
        from ....widgets.graphics.views.diagram import DiagramView, DiagramSubWindow
        from ....widgets.graphics.views.symbol  import SymbolView, SymbolSubWindow
        if not typeCheck(node, DesignDbNode | SymbolNode):
            return
        scene = node.scene()
        if isinstance(node, DesignDbNode):
            view = DiagramView(scene)
            subwindow = DiagramSubWindow(window().mdi_area)
        elif isinstance(node, SymbolNode):
            view = SymbolView(scene)
            subwindow = SymbolSubWindow(window().mdi_area)
        subwindow.setWidget(view)
        window().mdi_area.addSubWindow(subwindow)
        subwindow.showMaximized()
        window().mdi_area.activateSubWindow(subwindow)
        window().mdi_area.update()

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
        items = [e for e in scene.items() \
                    if not isinstance(e, Handle | Tether)]
        subwindow = SpreadsheetSubWindow(scene, items)
        subwindow.setWindowTitle(f"{db_node.text()}:{node.text()}: Properties")
        window().mdi_area.addSubWindow(subwindow)
        subwindow.showMaximized()
        window().menu_bar.updateWindowMenu()

    def _save(self : "Navigator", node : "DbNode") -> None:
        # TODO handle overwrite
        if node.path():
            node.save()
        else:
            self._saveAs(node)

    def _saveAs(self : "Navigator", node : "DbNode") -> None:
        from ...dialogs.file import FileSaveAsDialog
        dialog = FileSaveAsDialog(node.dbTypeName())
        result = dialog.exec()
        if result == dialog.DialogCode.Accepted:
            selected_files = dialog.selectedFiles()
            if len(selected_files) > 1:
                unexpected_files = list(selected_files[1:])
                logger().warning(f"Unexpected files: {unexpected_files}")
            path = selected_files[0]
            node.save(path)

    def _close(self : "Navigator", node : "DbNode") -> None:
        # TODO offer to save if modified
        model().close(node)
