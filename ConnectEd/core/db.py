import os

from typing import Self

from PyQt6.QtCore import Qt, QSize,QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtGui  import QStandardItemModel, QStandardItem

from ..app import logger, window

from ..resources import getIconPath

from ..core.icon import SvgIconSingleton

from .defs import LIB_EXT, DSN_EXT
from .xml  import copy, paste, fromXmlBegin, loadItems, saveBegin, saveEnd

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..widgets.graphics.scenes.drawing import DrawingScene
    from ..widgets.graphics.scenes.symbol  import SymbolScene
    from ..widgets.graphics.scenes.diagram import DiagramScene


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


class DiagramIcon(SvgIconSingleton):
    PATH = getIconPath("diagram.svg")
    SIZE = QSize(16, 16)


class SymbolIcon(SvgIconSingleton):
    PATH = getIconPath("symbol.svg")
    SIZE = QSize(16, 16)


class LibraryIcon(SvgIconSingleton):
    PATH = getIconPath("library.svg")
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


class DrawingNode(Node):
    @classmethod
    def sceneClass(cls):
        from ..widgets.graphics.scenes.drawing import DrawingScene
        return DrawingScene

    _scene : "DrawingScene | None"

    def __init__(
        self  : Self,
        scene : "DrawingScene | None" = None,
        bare  : bool = False
    ) -> None:
        if scene is None and not bare:
            scene_class = self.__class__.sceneClass()
            scene = scene_class()
            scene.setName(name_counter.get(self.drawingTypeName()))
        self._scene = scene
        super().__init__()
        if scene:
            super().setText(scene.name())
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsEditable)

    def setText(self : Self, text : str) -> None:
        super().setText(text)
        self._scene.setName(text)

    def scene(self : Self) -> "DrawingScene":
        return self._scene

    def setScene(self : Self, scene : "DrawingScene") -> None:
        self._scene = scene

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

    _scene : "SymbolScene | None"

    def __init__(self : Self, name : str | None = None) -> None:
        super().__init__(name)
        self.setIcon(SymbolIcon().get())

    def dbNode(self : Self) -> "DesignDbNode | LibraryDbNode":
        return self.parent()


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
        self.setToolTip("(not yet saved)")

    def dbTypeName(self) -> str:
        cls = self if isinstance(self, type) else self.__class__
        return cls.__name__.replace("DbNode", "")

    def path(self : Self) -> str:
        return self._path

    def setPath(self : Self, path : str) -> None:
        self._path = path
        self.setToolTip(path)

    def symbolNodes(self : Self) -> list[SymbolNode]:
        r = []
        for i in range(self.rowCount()):
            node = self.child(i)
            if isinstance(node, SymbolNode):
                r.append(node)
            else:
                logger().warning(f"Unexpected node: {node.text()} ({type(node)})")
        return r

    def newSymbolNode(self : Self) -> SymbolNode:
        item = SymbolNode()
        self.addSymbolNode(item)
        return item

    def addSymbolNode(self : Self, node : SymbolNode) -> None:
        self.appendRow(node)

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        raise NotImplementedError(
            f"Subclass {self.__class__.__name__} must implement toXml"
        )

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
        db_node = cls("")
        attributes = xr.attributes()
        for attribute in attributes:
            tag = attribute.name()
            value_str = attribute.value()
            if tag == "name":
                db_node.setText(value_str)
            else:
                logger().warning(f"Unexpected attribute: {tag} value: {value_str}")
        xr.readNext()
        return db_node

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


# TODO: reintroduce support for multiple diagrams?
class DesignDbNode(DbNode):
    FILE_EXT = DSN_EXT

    _scene   : "DiagramScene | None"

    def __init__(
        self : Self,
        name : str | None = None,
        bare : bool = False
    ) -> None:
        from ..widgets.graphics.scenes.diagram import DiagramScene
        self._scene = None if bare else DiagramScene()
        super().__init__(name)
        self.setIcon(DiagramIcon().get())

    def setText(self : Self, text : str) -> None:
        super().setText(text)
        if self._scene is not None:
            self._scene.setName(text)

    def scene(self : Self) -> "DiagramScene":
        return self._scene

    def setScene(self : Self, scene : "DiagramScene") -> None:
        self._scene = scene
        super().setText(scene.name())

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self.toXmlBegin(xw)
        xw.writeStartElement("Symbols")
        for i in range(self.rowCount()):
            symbol_node : SymbolNode = self.child(i)
            symbol_scene = symbol_node.scene()
            symbol_scene.toXml(xw)
        xw.writeEndElement()
        self.scene().toXml(xw)
        self.toXmlEnd(xw)

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        from ..widgets.graphics.scenes.diagram import DiagramScene
        db_node : Self = cls.fromXmlBegin(xr)
        while not (xr.isEndElement() and xr.name() == cls.dbTypeName(cls)):
            if xr.tokenType() == xr.TokenType.EndDocument:
                logger().error(f"End of document before end of '{cls.dbTypeName(cls)}'")
                break
            # process symbols
            if xr.name() == "Symbols" and xr.isStartElement():
                xr.readNext()  # move past <Symbols>
                while not (xr.isEndElement() and xr.name() == "Symbols"):
                    if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                        if xr.name() == "Symbol":
                            symbol_node = SymbolNode.fromXml(xr)
                            db_node.addSymbolNode(symbol_node)
                        else:
                            msg = f"Unexpected element in Symbols: {xr.name()}"
                            raise ValueError(msg)
                    xr.readNext()
            # process scene
            elif xr.name() == "Diagram" and xr.isStartElement():
                diagram_scene = DiagramScene.fromXml(xr)
                db_node.setScene(diagram_scene)
            xr.readNext()
        db_node.fromXmlEnd(xr)
        return db_node


class LibraryDbNode(DbNode):
    FILE_EXT = LIB_EXT

    def __init__(self : Self, name : str | None = None) -> None:
        super().__init__(name)
        self.setIcon(LibraryIcon().get())

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self.toXmlBegin(xw)
        for i in range(self.rowCount()):
            child = self.child(i)
            if isinstance(child, SymbolNode):
                child.toXml(xw)
            else:
                logger().warning(f"Unexpected node: {child.text()} ({type(child)})")
        self.toXmlEnd(xw)

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        db_node : Self = cls.fromXmlBegin(xr)
        while not (xr.isEndElement() and xr.name() == cls.dbTypeName(cls)):
            xr.readNext()
        return db_node


class Model(QStandardItemModel):
    _diagrams  : DesignDbContainer
    _libraries : LibraryDbContainer

    def __init__(self : Self) -> None:
        super().__init__()
        self.setHorizontalHeaderLabels(["Database Hierarchy"])
        self._diagrams = DesignDbContainer()
        self.appendRow(self._diagrams)
        self._libraries = LibraryDbContainer()
        self.appendRow(self._libraries)

    def designDbContainer(self : Self) -> DesignDbContainer:
        return self._diagrams

    def designDbNodes(self : Self) -> list[DesignDbNode]:
        return [self._diagrams.child(i) for i in range(self._diagrams.rowCount())]

    def newDesignDbNode(self : Self, name : str | None = None) -> DesignDbNode:
        node = DesignDbNode(name)
        self.addDesignDbNode(node)
        return node

    def addDesignDbNode(self : Self, node : DesignDbNode) -> None:
        self.designDbContainer().appendRow(node)

    def libraryDbContainer(self : Self) -> LibraryDbContainer:
        return self._libraries

    def libraryDbNodes(self : Self) -> list[LibraryDbNode]:
        return [self._libraries.child(i) for i in range(self._libraries.rowCount())]

    def newLibraryDbNode(self : Self, name : str | None = None) -> LibraryDbNode:
        node = LibraryDbNode(name)
        self.addLibraryDbNode(node)
        return node

    def addLibraryDbNode(self : Self, node : LibraryDbNode) -> None:
        self.libraryDbContainer().appendRow(node)

    def load(self : Self, path : str) -> DesignDbNode | LibraryDbNode | None:
        if self._alreadyLoaded(path):
            return None
        db_node = None
        if path.endswith(DSN_EXT):
            db_node = DesignDbNode.load(path)
            self._diagrams.appendRow(db_node)
        elif path.endswith(LIB_EXT):
            db_node = LibraryDbNode.load(path)
            self._libraries.appendRow(db_node)
        else:
            logger().warning(f"Unsupported file extension: {path}")
        return db_node

    def close(self : Self, node : DesignDbNode | LibraryDbNode) -> bool:
        """Close a database and remove it from the model."""
        if not node.model() or node.model() != self:
            logger().warning(f"Node not found in model: {node.text()} ({type(node)})")
            return False
        if not isinstance(node, DesignDbNode | LibraryDbNode):
            logger().warning(f"Unsupported node: {node.text()} ({type(node)})")
            return False
        if isinstance(node, DesignDbNode):
            window().mdi_area.closeScene(node.scene())
        elif isinstance(node, LibraryDbNode):
            for i in range(node.rowCount()):
                symbol_node = node.child(i)
                if isinstance(symbol_node, SymbolNode):
                    window().mdi_area.closeScene(symbol_node.scene())
        return self._removeNode(node)

    def copy(self : Self, item : Node) -> None:
        copy(item)

    def paste(self : Self, node : Node) -> None:
        paste_items, _ = paste()
        if paste_items:
            if isinstance(node, DesignDbContainer):
                valid_item_types = [DesignDbNode]
            elif isinstance(node, LibraryDbContainer):
                valid_item_types = [LibraryDbNode]
            elif isinstance(node, DesignDbNode | LibraryDbNode | SymbolNode):
                valid_item_types = [SymbolNode]
            else:
                raise ValueError(
                    f"Cannot paste into item: {node.text()} ({type(node)})"
                )
            invalid_item_types = []
            invalid_item_count = 0
            for paste_item in paste_items:
                if not any(isinstance(paste_item, t) for t in valid_item_types):
                    invalid_item_types.append(type(paste_item).__name__)
                    invalid_item_count += 1
                else:
                    base_name = paste_item.text()
                    existing_names = [
                        paste_item.child(i).text()
                        for i in range(paste_item.rowCount())
                    ]
                    if base_name in existing_names:
                        paste_item.setText(name_counter.get(base_name))
                    node.appendRow(paste_item)
            if invalid_item_count:
                # TODO message box
                n = invalid_item_count
                s = ", ".join(invalid_item_types)
                raise ValueError(f"{n} invalid items for paste operation: {s}")

    def getDbNodeFromScene(self : Self, scene : "DrawingScene") -> DbNode:
        for diagram_db_node in self.designDbNodes():
            if scene == diagram_db_node.scene():
                return diagram_db_node
            for symbol_node in diagram_db_node.symbolNodes():
                if scene == symbol_node.scene():
                    return diagram_db_node
        for library_db_node in self.libraryDbNodes():
            for symbol_node in library_db_node.symbolNodes():
                if scene == symbol_node.scene():
                    return library_db_node
        return None

    def _alreadyLoaded(self : Self, path : str) -> bool:
        for db_node in self.designDbNodes():
            if db_node._path == path:
                return True
        for db_node in self.libraryDbNodes():
            if db_node._path == path:
                return True
        return False

    def _removeNode(self : Self, node : Node) -> bool:
        if not node.model() or node.model() != self:
            logger().warning(f"Node not found in model: {node.text()} ({type(node)})")
            return False
        row = node.index().row()
        if row == -1:
            logger().warning(f"Node is detached: {node.text()} ({type(node)})")
            return False
        parent = node.parent()
        if parent is None:
            return self.removeRow(row)
        else:
            return parent.removeRow(row)
