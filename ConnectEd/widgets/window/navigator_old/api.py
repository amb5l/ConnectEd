from ....app import logger, model, settings

from ....core.check import checked
from ....core.utils import typeCheck

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....core.db import Node, DesignDbNode, LibraryDbNode, SymbolNode
    from ....widgets.graphics.scenes.drawing import DrawingScene
    from . import Navigator


class NavigatorApiMixin:

    ############################################################################
    # database methods

    def newDiagram(self : "Navigator") -> None:
        node = model().newDesignDbNode()
        self._editDrawing(node)

    def newLibrary(self : "Navigator") -> None:
        node = model().newLibraryDbNode()
        self.expand(model().indexFromItem(node))

    def open(self : "Navigator") -> None:
        self._open()

    def openDiagram(self : "Navigator") -> None:
        self._open("Diagram")

    def openLibrary(self : "Navigator") -> None:
        self._open("Library")

    @checked
    def load(self : "Navigator", path : str) -> None:
        if self._load(path) is not None:
            settings().addMRU(path)

    @checked
    def save(
        self : "Navigator",
        x    : "DesignDbNode | LibraryDbNode | SymbolNode | DrawingScene"
    ) -> None:
        from ....core.db import DesignDbNode, LibraryDbNode, SymbolNode
        from ....widgets.graphics.scenes.drawing import DrawingScene
        if not typeCheck(x, DesignDbNode | LibraryDbNode | SymbolNode | DrawingScene):
            return
        if isinstance(x, DrawingScene):
            x = model().getDbNodeFromScene(x)
        elif isinstance(x, SymbolNode):
            x = x.dbNode()
        if isinstance(x, DesignDbNode | LibraryDbNode):
            self._save(x)
        else:
            logger().warning(f"Unsupported node: {x.text()} ({type(x)})")
            return

    @checked
    def saveAs(
        self : "Navigator",
        x    : "DesignDbNode | LibraryDbNode | SymbolNode | DrawingScene"
    ) -> None:
        from ....core.db import DesignDbNode, LibraryDbNode, SymbolNode
        from ....widgets.graphics.scenes.drawing import DrawingScene
        if isinstance(x, DrawingScene):
            x = model().getDbNodeFromScene(x)
        elif isinstance(x, SymbolNode):
            x = x.dbNode()
        if isinstance(x, DesignDbNode | LibraryDbNode):
            self._saveAs(x)
        else:
            logger().warning(f"Unsupported node: {x.text()} ({type(x)})")
            return

    @checked
    def close(
        self : "Navigator",
        x    : "DesignDbNode | LibraryDbNode | SymbolNode | DrawingScene"
    ) -> None:
        from ....core.db import DesignDbNode, LibraryDbNode, SymbolNode
        from ....widgets.graphics.scenes.drawing import DrawingScene
        if isinstance(x, DrawingScene):
            x = model().getDbNodeFromScene(x)
        elif isinstance(x, SymbolNode):
            x = x.dbNode()
        if isinstance(x, DesignDbNode | LibraryDbNode):
            self._close(x)
        else:
            logger().warning(f"Unsupported node: {x.text()} ({type(x)})")
            return

    ############################################################################
    # drawing methods

    @checked
    def newSymbol(
        self : "Navigator",
        node : "DesignDbNode | LibraryDbNode | SymbolNode"
    ) -> None:
        from ....core.db import DesignDbNode, LibraryDbNode, SymbolNode
        if not typeCheck(node, DesignDbNode | LibraryDbNode | SymbolNode):
            return
        if isinstance(node, SymbolNode):
            node = node.dbNode()
        symbol_node = node.newSymbolNode()
        self.expand(model().indexFromItem(node))
        self._editDrawing(symbol_node)

    @checked
    def editDrawing(
        self : "Navigator",
        node : "DesignDbNode | SymbolNode"
    ) -> None:
        self._editDrawing(node)

    @checked
    def newDrawingWindow(self : "Navigator", node : "DesignDbNode") -> None:
        self._newDrawingWindow(node)

    @checked
    def editProperties(self : "Navigator", node : "DesignDbNode") -> None:
        from ....core.db import DesignDbNode
        if not typeCheck(node, DesignDbNode):
            return
        self._spreadsheet(node)

    @checked
    def setRoot(self : "Navigator", node : "DesignDbNode") -> None:
        from ....core.db import DesignDbNode
        if not typeCheck(node, DesignDbNode):
            return
        node.setRoot()

    ############################################################################
    # misc

    @checked
    def rename(self : "Navigator", node : "Node") -> None:
        self.edit(self.currentIndex())

    @checked
    def copy(self : "Navigator", node : "Node") -> None:
        model().copy(node)

    @checked
    def paste(self : "Navigator", node : "Node") -> None:
        model().paste(node)

    ############################################################################
