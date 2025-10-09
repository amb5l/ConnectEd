import os

from typing import Self

from PyQt6.QtCore    import Qt, QSize,QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtGui     import QStandardItemModel, QStandardItem

from ..app import logger

from ..resources import getIconPath

from ..core.icon import SvgIconSingleton

from .defs import LIB_EXT, DSN_EXT
from .xml  import copy, paste, fromXmlBegin, loadItems, saveBegin, saveEnd

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..widgets.graphics.scenes.drawing import DrawingScene
    from ..widgets.graphics.scenes.symbol  import SymbolScene
    from ..widgets.graphics.scenes.diagram import DiagramScene
    from ..widgets.graphics.views.drawing  import DrawingView, DrawingSubWindow


class NameCounter:
    counts : dict[str, int]

    def __init__(self : Self) -> None:
        self.counts = {}

    def get(self : Self, name : str) -> str:
        if name not in self.counts:
            self.counts[name] = 0
        self.counts[name] += 1
        return f"{name}{self.counts[name]}"

name_counter = NameCounter()


class RootIcon(SvgIconSingleton):
    PATH = getIconPath("root.svg")
    SIZE = QSize(16, 16)


class EmptyIcon(SvgIconSingleton):
    PATH = getIconPath("empty.svg")
    SIZE = QSize(16, 16)


class Node(QStandardItem):
    pass


class Container(Node):
    NAME   = "<unspecified>"
    BOLD   = False
    ITALIC = False

    def __init__(self : Self) -> None:
        super().__init__(self.NAME)
        font = self.font()
        font.setBold(self.BOLD)
        font.setItalic(self.ITALIC)
        self.setFont(font)


class DesignDbContainer(Container):
    NAME   = "Designs"
    BOLD   = True


class LibraryDbContainer(Container):
    NAME   = "Libraries"
    BOLD   = True


class DiagramsContainer(Container):
    NAME   = "Diagrams"
    ITALIC = True

    # instance attributes
    _root : "DiagramNode"

    def __init__(self : Self) -> None:
        super().__init__()
        self._root = None

    def root(self : Self) -> "DiagramNode":
        return self._root

    def setRoot(self : Self, item : "DiagramNode") -> None:
        if self._root is not None:
            self._root.setIcon(EmptyIcon().get())
        self._root = item
        if self._root is not None:
            icon = RootIcon().get()
            self._root.setIcon(icon)


class SymbolCacheContainer(Container):
    NAME   = "Symbol Cache"
    ITALIC = True


class DrawingNode(Node):
    @classmethod
    def sceneClass(cls):
        from ..widgets.graphics.scenes.drawing import DrawingScene
        return DrawingScene

    _scene : "DrawingScene"

    def __init__(self : Self, scene : "DrawingScene | None" = None) -> None:
        if scene is None:
            scene_class = self.__class__.sceneClass()
            scene = scene_class()
            scene.setName(name_counter.get(self.drawingTypeName()))
        self._scene = scene
        super().__init__()
        super().setText(scene.name())
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsEditable)

    def setText(self : Self, text : str) -> None:
        super().setText(text)
        self._scene.setName(text)

    def scene(self : Self) -> "DrawingScene":
        return self._scene

    def setScene(self : Self, scene : "DrawingScene") -> None:
        self._scene = scene

    def views(self : Self) -> list["DrawingView"]:
        return self._scene.views()

    def drawingTypeName(self : Self) -> str:
        return self.__class__.__name__.replace("Node", "")

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self._scene.toXml(xw)

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        scene : "DrawingScene" = cls.sceneClass().fromXml(xr)
        item : "DrawingNode" = cls(scene)
        return item

    copy = copy


class SymbolNode(DrawingNode):
    @classmethod
    def sceneClass(cls):
        from ..widgets.graphics.scenes.symbol import SymbolScene
        return SymbolScene

    _scene : "SymbolScene"

    def symbol(self : Self) -> "SymbolScene":
        return self._scene

    def dbNode(self : Self) -> "LibraryDbNode | DesignDbNode":
        """Symbols live in the Symbol Cache of a design, or in a library."""
        parent = self.parent()
        if isinstance(parent, SymbolCacheContainer):
            return parent.parent()
        else:
            return parent


class DiagramNode(DrawingNode):
    @classmethod
    def sceneClass(cls):
        from ..widgets.graphics.scenes.diagram import DiagramScene
        return DiagramScene

    _scene : "DiagramScene"

    def __init__(self : Self, scene : "DiagramScene | None" = None) -> None:
        super().__init__(scene)
        self.setIcon(EmptyIcon().get())

    def diagram(self : Self) -> "DiagramScene":
        return self._scene

    def dbNode(self : Self) -> "DesignDbNode":
        """
        For now, diagrams always live in a diagrams container under a design.
        """
        return self.parent().parent()


class DbNode(Node):
    _path : str | None

    def __init__(self : Self, name : str | None = None) -> None:
        if name is None:
            name = name_counter.get(
                "Untitled" + self.dbTypeName()
            )
        super().__init__(name)
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsEditable)
        self._path = None

    def dbTypeName(self) -> str:
        cls = self if isinstance(self, type) else self.__class__
        return cls.__name__.replace("DbNode", "")

    def path(self : Self) -> str:
        return self._path

    def setPath(self : Self, path : str) -> None:
        self._path = path

    def close(self : Self) -> None:  # TODO: needed?
        pass

    def toXmlBegin(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.dbTypeName())
        xw.writeAttribute("name", self.text())

    def toXmlEnd(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeEndElement()

    def save(self : Self, path : str) -> None:
        self.setPath(path)
        xw, file = saveBegin(self._path)
        self.toXml(xw)
        saveEnd(xw, file)

    @classmethod
    def fromXmlBegin(cls : Self, xr : QXmlStreamReader) -> Self:
        element_name = cls.dbTypeName(cls)
        if xr.name() == element_name and xr.isStartElement():
            pass  # Already at target element
        else:
            fromXmlBegin(xr, element_name)
        db_item = cls("")
        attributes = xr.attributes()
        for attribute in attributes:
            tag = attribute.name()
            value_str = attribute.value()
            if tag == "name":
                db_item.setText(value_str)
            else:
                logger().warning(f"Unexpected attribute: {tag} value: {value_str}")
        xr.readNext()
        return db_item

    def fromXmlEnd(self : Self, xr : QXmlStreamReader) -> None:
        while not (xr.isEndElement() and xr.name() == self.dbTypeName()):
            xr.readNext()

    @classmethod
    def load(cls : Self, path : str) -> Self:
        if not os.path.exists(path):
            logger().warning(f"{path} not found")
            return None
        items = loadItems(path)
        for item in items:
            if isinstance(item, cls):
                item._path = path
                return item
        logger().warning(f"{cls.__name__} not found in {path}")
        return None

    copy = copy


class DesignDbNode(DbNode):
    FILE_EXT = DSN_EXT

    _diagrams : DiagramsContainer
    _symbols  : SymbolCacheContainer

    def __init__(self : Self, name : str | None = None) -> None:
        super().__init__(name)
        self._diagrams = DiagramsContainer()
        self.appendRow(self._diagrams)
        self._symbols = SymbolCacheContainer()
        self.appendRow(self._symbols)

    def newDiagramNode(self : Self, name : str | None = None) -> DiagramNode:
        item = DiagramNode(name)
        self._diagrams.appendRow(item)
        if self._diagrams.root() is None:
            self._diagrams.setRoot(item)
        return item

    def diagramsNode(self : Self) -> DiagramsContainer:
        return self._diagrams

    def diagramNodes(self : Self) -> list[DiagramNode]:
        return [self._diagrams.child(i) for i in range(self._diagrams.rowCount())]

    def rootDiagramNode(self : Self) -> DiagramNode | None:
        if self._diagrams.root() is None:
            return None
        return self._diagrams.root()

    def newSymbolNode(self : Self, name : str | None = None) -> SymbolNode:
        item = SymbolNode(name)
        self._symbols.appendRow(item)
        return item

    def symbolsNode(self : Self) -> SymbolCacheContainer:
        return self._symbols

    def symbolNodes(self : Self) -> list[SymbolNode]:
        return [self._symbols.child(i) for i in range(self._symbols.rowCount())]

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self.toXmlBegin(xw)
        xw.writeStartElement("Diagrams")
        root = "" if self._diagrams.root() is None \
            else self._diagrams.root().text()
        xw.writeAttribute("root", root)
        for i in range(self._diagrams.rowCount()):
            diagram_node : DiagramNode = self._diagrams.child(i)
            diagram_scene = diagram_node._scene
            diagram_scene.toXml(xw)
        xw.writeEndElement()
        xw.writeStartElement("SymbolCache")
        for i in range(self._symbols.rowCount()):
            symbol_node : SymbolNode = self._symbols.child(i)
            symbol_scene = symbol_node._scene
            symbol_scene.toXml(xw)
        xw.writeEndElement()
        self.toXmlEnd(xw)

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        db_item : Self = cls.fromXmlBegin(xr)
        while not (xr.isEndElement() and xr.name() == cls.dbTypeName(cls)):
            if xr.tokenType() == xr.TokenType.EndDocument:
                logger().error(f"Reached end of document while looking for end of '{cls.dbTypeName(cls)}'")
                break
            if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                if xr.name() == "Diagrams":
                    root_name = ""
                    attributes = xr.attributes()
                    for attribute in attributes:
                        if attribute.name() == "root":
                            root_name = attribute.value()
                            break
                        else:
                            logger().warning(f"Unexpected attribute: {attribute.name()} value: {attribute.value()}")
                    xr.readNext()  # Move past <Diagrams>
                    while not (xr.isEndElement() and xr.name() == "Diagrams"):
                        if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                            if xr.name() == "Diagram":
                                diagram_node = DiagramNode.fromXml(xr)
                                db_item._diagrams.appendRow(diagram_node)
                            else:
                                raise ValueError(f"Unexpected element in Diagrams: {xr.name()}")
                        xr.readNext()
                    # Set the root diagram based on the loaded name
                    if root_name:
                        root = None
                        for i in range(db_item._diagrams.rowCount()):
                            diagram_node = db_item._diagrams.child(i)
                            if diagram_node.text() == root_name:
                                root = diagram_node
                                db_item._diagrams.setRoot(root)
                                break
                        if root is None:
                            logger().warning(f"Root diagram '{root_name}' not found, defaulting to first")
                            if db_item._diagrams.rowCount() > 0:
                                db_item._diagrams.setRoot(db_item._diagrams.child(0))
                    elif db_item._diagrams.rowCount() > 0:
                        db_item._diagrams.setRoot(db_item._diagrams.child(0))
                elif xr.name() == "SymbolCache":
                    xr.readNext()  # Move past <SymbolCache>
                    while not (xr.isEndElement() and xr.name() == "SymbolCache"):
                        if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                            if xr.name() == "Symbol":
                                symbol_node = SymbolNode.fromXml(xr)
                                db_item._symbols.appendRow(symbol_node)
                            else:
                                raise ValueError(f"Unexpected element in SymbolCache: {xr.name()}")
                        xr.readNext()
                else:
                    raise ValueError(f"Unexpected element in Design: {xr.name()}")
            xr.readNext()
        db_item.fromXmlEnd(xr)
        return db_item

    def diagramsNode(self : Self) -> DiagramsContainer:
        return self._diagrams

    def symbolsNode(self : Self) -> SymbolCacheContainer:
        return self._symbols

    def diagramNodes(self : Self) -> list[DiagramNode]:
        return [self._diagrams.child(i) for i in range(self._diagrams.rowCount())]

    def symbolNodes(self : Self) -> list[SymbolNode]:
        return [self._symbols.child(i) for i in range(self._symbols.rowCount())]


class LibraryDbNode(DbNode):
    FILE_EXT = LIB_EXT

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self.toXmlBegin(xw)
        for i in range(self.rowCount()):
            symbol_node : SymbolNode = self.child(i)
            symbol_scene = symbol_node._scene
            symbol_scene.toXml(xw)
        self.toXmlEnd(xw)

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        db_item : Self = cls.fromXmlBegin(xr)
        while not (xr.isEndElement() and xr.name() == cls.dbTypeName(cls)):
            xr.readNext()
        return db_item


class Model(QStandardItemModel):
    _designs   : DesignDbContainer
    _libraries : LibraryDbContainer

    def __init__(self : Self) -> None:
        super().__init__()
        self.setHorizontalHeaderLabels(["Database Hierarchy"])
        self._designs = DesignDbContainer()
        self.appendRow(self._designs)
        self._libraries = LibraryDbContainer()
        self.appendRow(self._libraries)

    def newDesignDbNode(self : Self, name : str | None = None) -> DesignDbNode:
        item = DesignDbNode(name)
        self._designs.appendRow(item)
        return item

    def newLibraryDbNode(self : Self, name : str | None = None) -> LibraryDbNode:
        item = LibraryDbNode(name)
        self._libraries.appendRow(item)
        return item

    def newDiagramNode(
        self   : Self,
        parent : Node,
        name   : str | None = None
    ) -> DiagramNode | None:
        item = None
        if isinstance(parent, DesignDbNode):
            parent = parent._diagrams
        if isinstance(parent, DiagramsContainer):
            item = DiagramNode(name)
            parent.appendRow(item)
        else:
            logger().warning(
                f"Unexpected parent item: {parent.text()} ({type(parent)})"
            )
        return item

    def newSymbolNode(
        self   : "Model",
        parent : Node
    ) -> SymbolNode | None:
        item = None
        if isinstance(parent, DesignDbNode):
            parent = parent._symbols
        if isinstance(parent, (SymbolCacheContainer, LibraryDbNode)):
            item = SymbolNode()
            parent.appendRow(item)
        else:
            logger().warning(
                f"Unexpected parent item: {parent.text()} ({type(parent)})"
            )
        return item

    def load(self : Self, path : str) -> DbNode | None:
        if self._alreadyLoaded(path):
            return None
        db_item = None
        if path.endswith(DSN_EXT):
            db_item = DesignDbNode.load(path)
            self._designs.appendRow(db_item)
        elif path.endswith(LIB_EXT):
            db_item = LibraryDbNode.load(path)
            self._libraries.appendRow(db_item)
        else:
            logger().warning(f"Unsupported file extension: {path}")
        return db_item

    def close(self : Self, item : Node) -> None:
        from ..widgets.window.sub_window import SubWindow
        """Close a database and remove it from the model."""
        if isinstance(item, DesignDbNode):
            # close all open diagram windows for this design
            for i in range(item._diagrams.rowCount()):
                diagram_node = item._diagrams.child(i)
                if isinstance(diagram_node, DiagramNode):
                    for view in diagram_node.views():
                        if view:
                            subwindow : DrawingSubWindow | None = \
                                view.parentWidget()
                            if subwindow:
                                subwindow.close()
            # close all open symbol windows for this design
            for i in range(item._symbols.rowCount()):
                symbol_node = item._symbols.child(i)
                if isinstance(symbol_node, SymbolNode):
                    for view in symbol_node.views():
                        if view:
                            subwindow : DrawingSubWindow | None = \
                                view.parentWidget()
                            if subwindow:
                                subwindow.close()
            # remove the design from the model
            for i in range(self._designs.rowCount()):
                if item == self._designs.child(i):
                    self._designs.removeRow(i)
                    break
        elif isinstance(item, LibraryDbNode):
            # close all open symbol windows for this library
            for i in range(item.rowCount()):
                symbol_node = item.child(i)
                if isinstance(symbol_node, SymbolNode):
                    for view in symbol_node.views():
                        if view:
                            # Find the parent SubWindow instead of using window()
                            subwindow = view.parentWidget()
                            while subwindow and not isinstance(subwindow, SubWindow):
                                subwindow = subwindow.parentWidget()
                            if subwindow:
                                subwindow.close()
            # remove the library from the model
            for i in range(self._libraries.rowCount()):
                if item == self._libraries.child(i):
                    self._libraries.removeRow(i)
                    break
        else:
            logger().warning(f"Unsupported item: {item.text()} ({type(item)})")

    def copy(self : Self, item : Node) -> None:
        copy(item)

    def paste(self : Self, item : Node) -> None:
        paste_items, _ = paste()
        if paste_items:
            match self.getNodeDescription(item):
                case "Designs":
                    valid_item_types = [DesignDbNode]
                case "Libraries":
                    valid_item_types = [LibraryDbNode]
                case "Diagrams":
                    valid_item_types = [DiagramNode]
                case "Symbol Cache":
                    valid_item_types = [SymbolNode]
                case _:
                    raise ValueError(
                        f"Cannot paste into item: {item.text()} ({type(item)})")
            invalid_item_types = []
            invalid_item_count = 0
            for paste_item in paste_items:
                if not any(isinstance(paste_item, t) for t in valid_item_types):
                    invalid_item_types.append(type(paste_item).__name__)
                    invalid_item_count += 1
                else:
                    base_name = paste_item.text()
                    existing_names = \
                        [paste_item.child(i).text() for i in range(paste_item.rowCount())]
                    if base_name in existing_names:
                        paste_item.setText(name_counter.get(base_name))
                    item.appendRow(paste_item)
            if invalid_item_count:
                # TODO message box
                n = invalid_item_count
                s = ", ".join(invalid_item_types)
                raise ValueError(f"{n} invalid items for paste operation: {s}")

    def getDbNodeFromScene(self : Self, scene : "DrawingScene") -> DbNode:
        for i in range(self._designs.rowCount()):
            design : DesignDbNode = self._designs.child(i)
            diagrams_item : DiagramsContainer = design.diagramsNode()
            for j in range(diagrams_item.rowCount()):
                drawing_item : DrawingNode = diagrams_item.child(j)
                if scene == drawing_item._scene:
                    return design
            symbols_item : SymbolCacheContainer = design.symbolsNode()
            for j in range(symbols_item.rowCount()):
                drawing_item : DrawingNode = symbols_item.child(j)
                if scene == drawing_item._scene:
                    return design
        for i in range(self._libraries.rowCount()):
            library : LibraryDbNode = self._libraries.child(i)
            for j in range(library.rowCount()):
                drawing_item : DrawingNode = library.child(j)
                if scene == drawing_item._scene:
                    return library
        return None

    def getNodeDescription(self : Self, i : Node) -> str | None:
        if isinstance(i, DesignDbNode):
            return "Design"
        elif isinstance(i, LibraryDbNode):
            return "Library"
        elif isinstance(i, DiagramNode):
            return "Diagram"
        elif isinstance(i, SymbolNode):
            if isinstance(i.parent(), Node) \
            and i.parent().text() == "Symbol Cache":
                return "Design Symbol"
            elif isinstance(i.parent(), LibraryDbNode):
                return "Library Symbol"
        elif isinstance(i, Node):
            if i.text() == "Designs":
                return "Designs"
            elif i.text() == "Libraries":
                return "Libraries"
            elif i.text() == "Diagrams":
                return "Diagrams"
            elif i.text() == "Symbol Cache":
                return "Symbol Cache"
        raise ValueError(f"Unsupported item: {i.text()}  type: {type(i)}")

    def designDbNodes(self : Self) -> list[DesignDbNode]:
        return [self._designs.child(i) for i in range(self._designs.rowCount())]

    def _alreadyLoaded(self : Self, path : str) -> bool:
        for i in range(self._designs.rowCount()):
            db_item : DesignDbNode = self._designs.child(i)
            if db_item._path == path:
                return True
        for i in range(self._libraries.rowCount()):
            db_item : LibraryDbNode = self._libraries.child(i)
            if db_item._path == path:
                return True
        return False
