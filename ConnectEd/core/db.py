from typing import Self

from PyQt6.QtCore import Qt, QSize,QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtGui  import QStandardItemModel, QStandardItem

from ..app import logger, window

from ..resources import getIconPath

from ..core.icon import SvgIconSingleton

from ..widgets.dialogs.file import FileSaveAsDialog

from .defs import LIB_EXT, DSN_EXT
from .xml  import copy, paste, fromXmlBegin, loadItems, saveBegin, saveEnd

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..widgets.graphics.scenes.drawing import DrawingScene
    from ..widgets.graphics.scenes.symbol  import SymbolScene
    from ..widgets.graphics.scenes.diagram import DiagramScene
    from ..widgets.graphics.views.drawing  import DrawingView


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


class Container(QStandardItem):
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
    _root : "DiagramItem"

    def __init__(self : Self) -> None:
        super().__init__()
        self._root = None

    @property
    def root(self : Self) -> "DiagramItem":
        return self._root

    @root.setter
    def root(self : Self, item : "DiagramItem") -> None:
        if self._root is not None:
            self._root.setIcon(EmptyIcon().get())
        self._root = item
        if self._root is not None:
            icon = RootIcon().get()
            self._root.setIcon(icon)


class SymbolCacheContainer(Container):
    NAME   = "Symbol Cache"
    ITALIC = True


class DrawingItem(QStandardItem):
    _scene_class = None

    @classmethod
    def sceneClass(cls):
        if cls._scene_class is None:
            from ..widgets.graphics.scenes import DrawingScene # deferred import
            cls._scene_class = DrawingScene
        return cls._scene_class

    _scene : "DrawingScene"

    def __init__(
        self  : Self,
        name  : str | None = None,
        scene : "DrawingScene | None" = None
    ) -> None:
        if name is None:
            name = name_counter.get(
                f"Untitled{self.__class__.__name__.replace('Item', '')}"
            )
        super().__init__(name)
        scene_class = self.__class__.sceneClass()
        if scene:
            scene.setParent(self)
        else:
            scene = scene_class(self)
        scene.name = name
        self._scene = scene
        self.setData(self._scene, Qt.ItemDataRole.UserRole)
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsEditable)

    def text(self : Self) -> str:
        return self._scene.name if self._scene else ""

    def setText(self : Self, text : str) -> None:
        self._scene.name = text

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self._scene.toXml(xw)

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        scene : "DrawingScene" = cls.sceneClass().fromXml(xr)
        instance : "DrawingItem" = cls(None, scene)
        scene.setParent(instance)
        return instance

    copy = copy

    def name(self : Self) -> str:
        return self.text()

    def scene(self : Self) -> "DrawingScene":
        return self._scene

    def views(self : Self) -> list["DrawingView"]:
        return self._scene.views()


class SymbolItem(DrawingItem):
    @classmethod
    def sceneClass(cls):
        if cls._scene_class is None:
            from ..widgets.graphics.scenes.symbol import SymbolScene # deferred import
            cls._scene_class = SymbolScene
        return cls._scene_class

    _scene : "SymbolScene"

    def symbol(self : Self) -> "SymbolScene":
        return self._scene

class DiagramItem(DrawingItem):
    @classmethod
    def sceneClass(cls):
        if cls._scene_class is None:
            from ..widgets.graphics.scenes.diagram import DiagramScene # deferred import
            cls._scene_class = DiagramScene
        return cls._scene_class

    _scene : "DiagramScene"

    def __init__(
        self  : Self,
        name  : str | None = None,
        scene : "DiagramScene | None" = None
    ) -> None:
        super().__init__(name, scene)
        self.setIcon(EmptyIcon().get())

    def diagram(self : Self) -> "DiagramScene":
        return self._scene

class DbItem(QStandardItem):
    _path : str | None

    def __init__(self : Self) -> None:
        u = "Untitled" + self.__class__.__name__.replace("DbItem", "")
        super().__init__(name_counter.get(u))
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsEditable)
        self._path = None

    def toXmlBegin(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__.replace("DbItem", ""))
        xw.writeAttribute("name", self.text())

    def toXmlEnd(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeEndElement()

    def save(self : Self, path : str | None = None) -> None:
        self._path = path
        if self._path is None:
            self._path = self.saveAs()
        if self._path:
            xw, file = saveBegin(self._path)
            self.toXml(xw)
            saveEnd(xw, file)

    def saveAs(self : Self) -> str:
        dialog = FileSaveAsDialog(self.__class__.__name__, window())
        path = None
        if dialog.exec():
            path, _ = dialog.getSaveFileName()
        return path

    @classmethod
    def fromXmlBegin(cls : Self, xr : QXmlStreamReader) -> Self:
        element_name = cls.__name__.replace("DbItem", "")
        if xr.name() == element_name and xr.isStartElement():
            pass  # Already at target element
        else:
            fromXmlBegin(xr, element_name)
        if cls.__name__ == 'DesignDbItem':
            db_item = cls(new=False)
        else:
            db_item = cls()
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
        while not (xr.isEndElement() and xr.name() == self.__class__.__name__.replace("DbItem", "")):
            xr.readNext()

    @classmethod
    def load(cls : Self, file : str) -> Self:
        items = loadItems(file)
        for item in items:
            if isinstance(item, cls):
                return item
        logger().warning(f"{cls.__name__} not found in {file}")
        return None

    copy = copy

    def getPath(self : Self) -> str:
        return self._path


class DesignDbItem(DbItem):
    FILE_EXT = DSN_EXT

    _diagrams : DiagramsContainer
    _symbols  : SymbolCacheContainer

    def __init__(self : Self, new : bool = True) -> None:
        super().__init__()
        self._diagrams = DiagramsContainer()
        self.appendRow(self._diagrams)
        self._symbols = SymbolCacheContainer()
        self.appendRow(self._symbols)
        if new:
            self._diagrams.appendRow(DiagramItem())
            self._diagrams.root = self._diagrams.child(0)
        else:
            self._diagrams.root = None

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self.toXmlBegin(xw)
        xw.writeStartElement("Diagrams")
        root = "" if self._diagrams.root is None else self._diagrams.root.text()
        xw.writeAttribute("root", root)
        for i in range(self._diagrams.rowCount()):
            diagram_item : DiagramItem = self._diagrams.child(i)
            diagram_scene = diagram_item._scene
            diagram_scene.toXml(xw)
        xw.writeEndElement()
        xw.writeStartElement("SymbolCache")
        for i in range(self._symbols.rowCount()):
            symbol_item : SymbolItem = self._symbols.child(i)
            symbol_scene = symbol_item._scene
            symbol_scene.toXml(xw)
        self.toXmlEnd(xw)

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        db_item = cls.fromXmlBegin(xr)
        while not (xr.isEndElement() and xr.name() == cls.__name__.replace("DbItem", "")):
            if xr.tokenType() == xr.TokenType.EndDocument:
                logger().error(f"DesignDbItem.fromXml: Reached end of document while looking for end of '{cls.__name__.replace('DbItem', '')}'")
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
                                diagram_item = DiagramItem.fromXml(xr)
                                db_item.diagrams.appendRow(diagram_item)
                            else:
                                raise ValueError(f"Unexpected element in Diagrams: {xr.name()}")
                        xr.readNext()
                    # Set the root diagram based on the loaded name
                    if root_name:
                        root = None
                        for i in range(db_item.diagrams.rowCount()):
                            diagram_item = db_item.diagrams.child(i)
                            if diagram_item.text() == root_name:
                                root = diagram_item
                                db_item.diagrams.root = root
                                break
                        if root is None:
                            logger().warning(f"DesignDbItem.fromXml: Root diagram '{root_name}' not found, defaulting to first")
                            if db_item.diagrams.rowCount() > 0:
                                db_item.diagrams.root = db_item.diagrams.child(0)
                    elif db_item.diagrams.rowCount() > 0:
                        db_item.diagrams.root = db_item.diagrams.child(0)
                elif xr.name() == "SymbolCache":
                    xr.readNext()  # Move past <SymbolCache>
                    while not (xr.isEndElement() and xr.name() == "SymbolCache"):
                        if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                            if xr.name() == "Symbol":
                                symbol_item = SymbolItem.fromXml(xr)
                                db_item.symbols.appendRow(symbol_item)
                            else:
                                raise ValueError(f"Unexpected element in SymbolCache: {xr.name()}")
                        xr.readNext()
                else:
                    raise ValueError(f"Unexpected element in Design: {xr.name()}")
            xr.readNext()
        db_item.fromXmlEnd(xr)
        return db_item

    def diagramsItem(self : Self) -> DiagramsContainer:
        return self._diagrams

    def symbolsItem(self : Self) -> SymbolCacheContainer:
        return self._symbols

    def diagramItems(self : Self) -> list[DiagramItem]:
        return [self._diagrams.child(i) for i in range(self._diagrams.rowCount())]

    def symbolItems(self : Self) -> list[SymbolItem]:
        return [self._symbols.child(i) for i in range(self._symbols.rowCount())]


class LibraryDbItem(DbItem):
    FILE_EXT = LIB_EXT

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self.toXmlBegin(xw)
        for i in range(self.rowCount()):
            symbol_item : SymbolItem = self.child(i)
            symbol_scene = symbol_item._scene
            symbol_scene.toXml(xw)
        self.toXmlEnd(xw)

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        db_item = cls.fromXmlBegin(xr)
        while not (xr.isEndElement() and xr.name() == cls.__name__.replace("DbItem", "")):
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

    def newDesignItem(self : Self) -> DesignDbItem:
        item = DesignDbItem()
        self._designs.appendRow(item)
        return item

    def newLibraryItem(self : Self) -> LibraryDbItem:
        item = LibraryDbItem()
        self._libraries.appendRow(item)
        return item

    def newDiagramItem(
        self   : Self,
        parent : QStandardItem
    ) -> DiagramItem | None:
        item = None
        if isinstance(parent, DesignDbItem):
            parent = parent._diagrams
        if isinstance(parent, DiagramsContainer):
            item = DiagramItem()
            parent.appendRow(item)
        else:
            logger().warning(
                f"Unexpected parent item: {parent.text()} ({type(parent)})"
            )
        return item

    def newSymbolItem(
        self   : "Model",
        parent : QStandardItem
    ) -> SymbolItem | None:
        item = None
        if isinstance(parent, DesignDbItem):
            parent = parent._symbols
        if isinstance(parent, (SymbolCacheContainer, LibraryDbItem)):
            item = SymbolItem()
            parent.appendRow(item)
        else:
            logger().warning(
                f"Unexpected parent item: {parent.text()} ({type(parent)})"
            )
        return item

    def load(self : Self, path : str) -> DbItem:
        db_item = None
        if path.endswith(DSN_EXT):
            db_item = DesignDbItem.load(path)
            self._designs.appendRow(db_item)
        elif path.endswith(LIB_EXT):
            db_item = LibraryDbItem.load(path)
            self._libraries.appendRow(db_item)
        else:
            logger().warning(f"Unsupported file extension: {path}")
        return db_item

    def close(self : Self, item: QStandardItem) -> None:
        """Close a database and remove it from the model."""
        if isinstance(item, DesignDbItem):
            for i in range(self._designs.rowCount()):
                if item == self._designs.child(i):
                    self._designs.removeRow(i)
        elif isinstance(item, LibraryDbItem):
            for i in range(self._libraries.rowCount()):
                if item == self._libraries.child(i):
                    self._libraries.removeRow(i)
        else:
            logger().warning(f"Unsupported item: {item.text()} ({type(item)})")

    def copy(self : Self, item : QStandardItem) -> None:
        copy(item)

    def paste(self : Self, item : QStandardItem) -> None:
        paste_items, _ = paste()
        if paste_items:
            match self.getItemDescription(item):
                case "Designs":
                    valid_item_types = [DesignDbItem]
                case "Libraries":
                    valid_item_types = [LibraryDbItem]
                case "Diagrams":
                    valid_item_types = [DiagramItem]
                case "Symbol Cache":
                    valid_item_types = [SymbolItem]
                case _:
                    raise ValueError(
                        f"Cannot paste into item: {paste_item.text()} ({type(paste_item)})")
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

    def getDbItemFromScene(self : Self, scene : "DrawingScene") -> DbItem:
        for i in range(self._designs.rowCount()):
            db_item : DesignDbItem = self._designs.child(i)
            diagrams_item : DiagramsContainer = db_item.diagramsItem()
            for j in range(diagrams_item.rowCount()):
                drawing_item : DrawingItem = diagrams_item.child(j)
                if scene == drawing_item._scene:
                    return db_item
            symbols_item : SymbolCacheContainer = db_item.symbolsItem()
            for j in range(symbols_item.rowCount()):
                drawing_item : DrawingItem = symbols_item.child(j)
                if scene == drawing_item._scene:
                    return db_item
        for i in range(self._libraries.rowCount()):
            db_item : LibraryDbItem = self._libraries.child(i)
            for j in range(db_item.rowCount()):
                drawing_item : DrawingItem = db_item.child(j)
                if scene == drawing_item._scene:
                    return db_item
        return None

    def getItemDescription(self : Self, i : QStandardItem) -> str | None:
        if isinstance(i, DesignDbItem):
            return "Design"
        elif isinstance(i, LibraryDbItem):
            return "Library"
        elif isinstance(i, DiagramItem):
            return "Diagram"
        elif isinstance(i, SymbolItem):
            if isinstance(i.parent(), QStandardItem) \
            and i.parent().text() == "Symbol Cache":
                return "Design Symbol"
            elif isinstance(i.parent(), LibraryDbItem):
                return "Library Symbol"
        elif isinstance(i, QStandardItem):
            if i.text() == "Designs":
                return "Designs"
            elif i.text() == "Libraries":
                return "Libraries"
            elif i.text() == "Diagrams":
                return "Diagrams"
            elif i.text() == "Symbol Cache":
                return "Symbol Cache"
        raise ValueError(f"Unsupported item: {i.text()}  type: {type(i)}")

    def designItems(self : Self) -> list[DesignDbItem]:
        return [self._designs.child(i) for i in range(self._designs.rowCount())]
