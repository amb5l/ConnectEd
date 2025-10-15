from ....app import logger, model

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....core.db import Node, \
                            DesignDbNode, LibraryDbNode, \
                            DiagramsContainer, SymbolsContainer, \
                            DiagramNode, SymbolNode, \
                            DrawingWindowNode
    from ....widgets.graphics.scenes.drawing import DrawingScene
    from ....widgets.graphics.scenes.diagram import DiagramScene
    from . import Navigator


class NavigatorApiMixin:

    ############################################################################
    # database methods

    def newDesign(self : "Navigator") -> None:
        design_db_node = model().newDesignDbNode()
        diagram_node = design_db_node.newDiagramNode()
        self.expand(model().indexFromItem(design_db_node))
        self.expand(model().indexFromItem(design_db_node.diagramsContainer()))
        self._editDrawing(diagram_node)

    def newLibrary(self : "Navigator") -> None:
        library_db_node = model().newLibraryDbNode()
        self.expand(model().indexFromItem(library_db_node))

    def open(self : "Navigator") -> None:
        self._openDb()

    def openDesign(self : "Navigator") -> None:
        self._openDb("Design")

    def openLibrary(self : "Navigator") -> None:
        self._openDb("Library")

    def openFile(self : "Navigator", path : str) -> None:
        self._openDbFile(path)

    def save(
        self : "Navigator",
        x    : "DesignDbNode | LibraryDbNode | DrawingScene"
    ) -> None:
        if isinstance(x, DrawingScene):
            x = model().getDbNodeFromScene(x)
        if isinstance(x, DesignDbNode):
            self._save(x)
        else:
            logger().warning(f"Unsupported node: {x.text()} ({type(x)})")
            return

    def saveAs(
        self : "Navigator",
        x    : "DesignDbNode | LibraryDbNode | DrawingScene"
    ) -> None:
        if isinstance(x, DrawingScene):
            x = model().getDbNodeFromScene(x)
        if isinstance(x, DesignDbNode):
            self._saveAs(x)
        else:
            logger().warning(f"Unsupported node: {x.text()} ({type(x)})")
            return

    def close(
        self : "Navigator",
        x    : "DesignDbNode | LibraryDbNode | DrawingScene"
    ) -> None:
        if isinstance(x, DrawingScene):
            x = model().getDbNodeFromScene(x)
        if isinstance(x, DesignDbNode):
            self._close(x)
        else:
            logger().warning(f"Unsupported node: {x.text()} ({type(x)})")
            return

    ############################################################################
    # drawing methods

    def newDiagram(
        self : "Navigator",
        node : "DesignDbNode | DiagramsContainer | DiagramNode"
    ) -> None:
        from ....core.db import DesignDbNode, DiagramsContainer, DiagramNode
        if not self._nodeTypeOK(
            node, DesignDbNode | DiagramsContainer | DiagramNode
        ):
            return
        if isinstance(node, DiagramNode):
            node = node.parent()
        if isinstance(node, DiagramsContainer):
            node = node.parent()
        diagram_node = model().newDiagramNode(node)
        self.expand(model().indexFromItem(diagram_node))
        self._editDrawing(diagram_node)

    def newSymbol(
        self : "Navigator",
        node : "LibraryDbNode | SymbolsContainer | SymbolNode"
    ) -> None:
        from ....core.db import LibraryDbNode, SymbolsContainer, SymbolNode
        if not self._nodeTypeOK(
            node, LibraryDbNode | SymbolsContainer | SymbolNode
        ):
            return
        if isinstance(node, SymbolNode):
            node = node.parent()
        if isinstance(node, SymbolsContainer):
            node = node.parent()
        symbol_node = model().newSymbolNode(node)
        self.expand(model().indexFromItem(symbol_node))
        self._editDrawing(symbol_node)

    def editDrawing(
        self : "Navigator",
        node : "DiagramNode | SymbolNode"
    ) -> None:
        from ....core.db import DiagramNode, SymbolNode
        if not self._nodeTypeOK(node, DiagramNode | SymbolNode):
            return
        self._editDrawing(node)

    def newDrawingWindow(self : "Navigator", node : "DiagramNode") -> None:
        print("newDiagramWindow")
        from ....core.db import DiagramNode
        if not self._nodeTypeOK(node, DiagramNode):
            return
        node.newWindow()
        self._updateWindowTitles(node)

    def editProperties(self : "Navigator", node : "DiagramNode") -> None:
        from ....core.db import DiagramNode
        if not self._nodeTypeOK(node, DiagramNode):
            return
        self._spreadsheet(node)

    def setRoot(self : "Navigator", node : "DiagramNode") -> None:
        from ....core.db import DiagramNode
        if not self._nodeTypeOK(node, DiagramNode):
            return
        node.setRoot()

    ############################################################################
    # drawing window methods

    def activateDrawingWindow(self : "Navigator", node : "DrawingWindowNode") -> None:
        from ....core.db import DrawingWindowNode
        if not self._nodeTypeOK(node, DrawingWindowNode):
            return
        node.activate()

    ############################################################################
    # misc

    def rename(
        self : "Navigator",
        node : "DesignDbNode | LibraryDbNode | DiagramNode | SymbolNode"
    ) -> None:
        if not self._nodeTypeOK(
            node,
            DesignDbNode | LibraryDbNode | DiagramNode | SymbolNode
        ):
            return
        self.edit(self.currentIndex())

    def copy(self : "Navigator", node : "Node") -> None:
        model().copy(node)

    def paste(self : "Navigator", node : "Node") -> None:
        model().paste(node)

    ############################################################################
