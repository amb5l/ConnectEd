__all__ = [
    "Drawing", "Symbol", "Diagram", "Db", "DesignDb", "LibraryDb", "Model"
]

from typing import Self, Optional

from PyQt6.QtCore import Qt, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtGui  import QStandardItemModel, QStandardItem

from .. import hub

from ..widgets import FileSaveAsDialog

from . import logger, \
              LIB_EXT, DSN_EXT, \
              copy, paste, fromXmlBegin, loadItems, saveBegin, saveEnd, \
              toXmlAttrs, fromXmlAttrs

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..widgets import DrawingScene, SymbolScene, DiagramScene


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

class DiagramsContainer(Container):
    NAME   = "Diagrams"
    ITALIC = True

class SymbolCacheContainer(Container):
    NAME   = "Symbol Cache"
    ITALIC = True

class DesignDbContainer(Container):
    NAME   = "Designs"
    BOLD   = True

class LibraryDbContainer(Container):
    NAME   = "Libraries"
    BOLD   = True

class Drawing(QStandardItem):
    _scene_class = None

    @classmethod
    def sceneClass(cls):
        if cls._scene_class is None:
            from ..widgets.drawing.scenes import DrawingScene # deferred import
            cls._scene_class = DrawingScene
        return cls._scene_class

    scene : "DrawingScene"

    def __init__(
        self  : Self,
        name  : Optional[str] = None,
        scene : Optional["DrawingScene"] = None
    ) -> None:
        if name is None:
            name = hub.name_counter.get(f"Untitled{self.__class__.__name__}")
        super().__init__(name)
        scene_class = self.__class__.sceneClass()
        if scene:
            scene.setParent(self)
        else:
            scene = scene_class(self)
        self.scene = scene
        self.setData(self.scene, Qt.ItemDataRole.UserRole)
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsEditable)

    copy = copy

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__)
        xw.writeAttribute("name", self.text())
        self.scene.toXml(xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        cls_name = cls.__name__
        if xr.name() != cls_name:
            raise ValueError(f"Expected {cls_name} element, got {xr.name()}")
        attributes = xr.attributes()
        for attr in attributes:
            if attr.name() == "name":
                name = attr.value()
        xr.readNext()
        while not (xr.isEndElement() and xr.name() == cls_name):
            if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                scene_class = cls.sceneClass()
                scene = scene_class.fromXml(xr)
                instance : "Drawing" = cls(name, scene)
                scene.setParent(instance)
                return instance
            xr.readNext()
        raise ValueError(f"No scene element found in {cls_name}")

    def getName(self : Self) -> str:
        return self.text()

    def getScene(self : Self) -> "DrawingScene":
        return self.scene

class Symbol(Drawing):
    @classmethod
    def sceneClass(cls):
        if cls._scene_class is None:
            from ..widgets.drawing.scenes import SymbolScene # deferred import
            cls._scene_class = SymbolScene
        return cls._scene_class

    scene : "SymbolScene"

class Diagram(Drawing):
    @classmethod
    def sceneClass(cls):
        if cls._scene_class is None:
            from ..widgets.drawing.scenes import DiagramScene # deferred import
            cls._scene_class = DiagramScene
        return cls._scene_class

    scene : "DiagramScene"

class Db(QStandardItem):
    _XML_ATTRS = {
        "name" : (
            "str",
            lambda self: True,
            lambda self, value: self.setText(value),
            lambda self: self.text()
        )
    }

    path : Optional[str]

    def __init__(self : Self) -> None:
        u = "Untitled" + self.__class__.__name__.replace("Db", "")
        super().__init__(hub.name_counter.get(u))
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsEditable)
        self.path = None

    @classmethod
    def fromXmlBegin(cls : Self, xr : QXmlStreamReader) -> Self:
        fromXmlBegin(xr, cls.__name__.replace("Item", ""))
        db_item = cls()
        fromXmlAttrs(db_item, xr)
        return db_item

    def fromXmlEnd(self : Self, xr : QXmlStreamReader) -> None:
        while not (xr.isEndElement() and xr.name() == self.__class__.__name__.replace("Item", "")):
            xr.readNext()

    def toXmlBegin(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__.replace("Item", ""))
        toXmlAttrs(self, xw)

    def toXmlEnd(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeEndElement()

    @classmethod
    def load(cls : Self, file : str) -> Self:
        items = loadItems(file)
        for item in items:
            if isinstance(item, cls):
                return item
        logger.warning(f"{cls.__name__} not found in {file}")
        return None

    def save(self : Self, path : Optional[str] = None) -> None:
        self.path = path
        if self.path is None:
            self.path = self.saveAs()
        if self.path:
            xw, file = saveBegin(self.path)
            self.toXml(xw)
            saveEnd(xw, file)

    def saveAs(self : Self) -> str:
        dialog = FileSaveAsDialog(self.__class__.__name__)
        path = None
        if dialog.exec():
            path, _ = dialog.getSaveFileName()
        return path

    copy = copy

    def getPath(self : Self) -> str:
        return self.path

class LibraryDb(Db):
    FILE_EXT = LIB_EXT

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self.toXmlBegin(xw)
        for i in range(self.rowCount()):
            symbol_item : Symbol = self.child(i)
            symbol_scene = symbol_item.scene
            symbol_scene.toXml(xw)
        self.toXmlEnd(xw)

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        db_item = cls.fromXmlBegin(xr)
        while not (xr.isEndElement() and xr.name() == cls.__name__.replace("Item", "")):
            xr.readNext()
        return db_item

class DesignDb(Db):
    FILE_EXT = DSN_EXT

    diagrams : DiagramsContainer
    symbols  : SymbolCacheContainer

    def __init__(self : Self) -> None:
        super().__init__()
        self.diagrams = DiagramsContainer()
        self.appendRow(self.diagrams)
        self.symbols = SymbolCacheContainer()
        self.appendRow(self.symbols)
        self.diagrams.appendRow(Diagram())

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        db_item = cls.fromXmlBegin(xr)
        while not (xr.isEndElement() and xr.name() == cls.__name__.replace("Item", "")):
            if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                if xr.name() == "Diagrams":
                    xr.readNext()  # Move past <Diagrams>
                    while not (xr.isEndElement() and xr.name() == "Diagrams"):
                        if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                            if xr.name() == "Diagram":
                                diagram_item = Diagram.fromXml(xr)
                                db_item.diagrams.appendRow(diagram_item)
                            else:
                                raise ValueError(f"Unexpected element in Diagrams: {xr.name()}")
                        xr.readNext()
                elif xr.name() == "SymbolCache":
                    xr.readNext()  # Move past <SymbolCache>
                    while not (xr.isEndElement() and xr.name() == "SymbolCache"):
                        if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                            if xr.name() == "Symbol":
                                symbol_item = Symbol.fromXml(xr)
                                db_item.symbols.appendRow(symbol_item)
                            else:
                                raise ValueError(f"Unexpected element in SymbolCache: {xr.name()}")
                        xr.readNext()
                else:
                    raise ValueError(f"Unexpected element in Design: {xr.name()}")
            xr.readNext()
        db_item.fromXmlEnd(xr)
        return db_item

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self.toXmlBegin(xw)
        xw.writeStartElement("Diagrams")
        for i in range(self.diagrams.rowCount()):
            diagram_item : Diagram = self.diagrams.child(i)
            diagram_scene = diagram_item.scene
            diagram_scene.toXml(xw)
        xw.writeEndElement()
        xw.writeStartElement("SymbolCache")
        for i in range(self.symbols.rowCount()):
            symbol_item : Symbol = self.symbols.child(i)
            symbol_scene = symbol_item.scene
            symbol_scene.toXml(xw)
        self.toXmlEnd(xw)

    def getDiagrams(self : Self) -> list[Diagram]:
        return [self.diagrams.child(i) for i in range(self.diagrams.rowCount())]

    def getSymbols(self : Self) -> list[Symbol]:
        return [self.symbols.child(i) for i in range(self.symbols.rowCount())]

class Model(QStandardItemModel):
    designs   : DesignDbContainer
    libraries : LibraryDbContainer

    def __init__(self : Self) -> None:
        super().__init__()
        self.setHorizontalHeaderLabels(["Database Hierarchy"])
        self.designs = DesignDbContainer()
        self.appendRow(self.designs)
        self.libraries = LibraryDbContainer()
        self.appendRow(self.libraries)

    def newDesign(self : Self) -> DesignDb:
        item = DesignDb()
        self.designs.appendRow(item)
        return item

    def newLibrary(self : Self) -> LibraryDb:
        item = LibraryDb()
        self.libraries.appendRow(item)
        return item

    def newDiagram(
        self   : Self,
        parent : QStandardItem
    ) -> Diagram | None:
        item = None
        if isinstance(parent, DesignDb):
            parent = parent.diagrams
        if isinstance(parent, DiagramsContainer):
            item = Diagram()
            parent.appendRow(item)
        else:
            logger.warning(
                f"Unexpected parent item: {parent.text()} ({type(parent)})"
            )
        return item

    def newSymbol(
        self   : "Model",
        parent : QStandardItem
    ) -> Symbol | None:
        item = None
        if isinstance(parent, DesignDb):
            parent = parent.symbols
        if isinstance(parent, (SymbolCacheContainer, LibraryDb)):
            item = Symbol()
            parent.appendRow(item)
        else:
            logger.warning(
                f"Unexpected parent item: {parent.text()} ({type(parent)})"
            )
        return item

    def load(self : Self, path : str) -> Db:
        db_item = None
        if path.endswith(DSN_EXT):
            db_item = DesignDb.load(path)
            self.designs.appendRow(db_item)
        elif path.endswith(LIB_EXT):
            db_item = LibraryDb.load(path)
            self.libraries.appendRow(db_item)
        else:
            logger.warning(f"Unsupported file extension: {path}")
        return db_item

    def close(self : Self, item: QStandardItem) -> None:
        """Close a database and remove it from the model."""
        if isinstance(item, DesignDb):
            for i in range(self.designs.rowCount()):
                if item == self.designs.child(i):
                    self.designs.removeRow(i)
        elif isinstance(item, LibraryDb):
            for i in range(self.libraries.rowCount()):
                if item == self.libraries.child(i):
                    self.libraries.removeRow(i)
        else:
            logger.warning(f"Unsupported item: {item.text()} ({type(item)})")

    def copy(self : Self, item : QStandardItem) -> None:
        copy(item)

    def paste(self : Self, item : QStandardItem) -> None:
        paste_items, _ = paste()
        if paste_items:
            match self.getItemDescription(item):
                case "Designs":
                    valid_item_types = [DesignDb]
                case "Libraries":
                    valid_item_types = [LibraryDb]
                case "Diagrams":
                    valid_item_types = [Diagram]
                case "Symbol Cache":
                    valid_item_types = [Symbol]
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
                        paste_item.setText(hub.name_counter.get(base_name))
                    item.appendRow(paste_item)
            if invalid_item_count:
                # TODO message box
                n = invalid_item_count
                s = ", ".join(invalid_item_types)
                raise ValueError(f"{n} invalid items for paste operation: {s}")

    def getDbItemFromScene(self : Self, scene : "DrawingScene") -> Db:
        for i in range(self.designs.rowCount()):
            db_item = self.designs.child(i)
            for j in range(db_item.diagrams.rowCount()):
                drawing_item : Drawing = db_item.diagrams.child(j)
                if scene == drawing_item.scene:
                    return db_item
            for j in range(db_item.symbols.rowCount()):
                drawing_item : Drawing = db_item.symbols.child(j)
                if scene == drawing_item.scene:
                    return db_item
        for i in range(self.libraries.rowCount()):
            db_item = self.libraries.child(i)
            for j in range(db_item.rowCount()):
                drawing_item : Drawing = db_item.child(j)
                if scene == drawing_item.scene:
                    return db_item
        return None

    def getItemDescription(self : Self, i : QStandardItem) -> str | None:
        if isinstance(i, DesignDb):
            return "Design"
        elif isinstance(i, LibraryDb):
            return "Library"
        elif isinstance(i, Diagram):
            return "Diagram"
        elif isinstance(i, Symbol):
            if isinstance(i.parent(), QStandardItem) \
            and i.parent().text() == "Symbol Cache":
                return "Design Symbol"
            elif isinstance(i.parent(), LibraryDb):
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
