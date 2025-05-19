__all__ = [
    "DrawingItem", "SymbolItem", "DiagramItem",
    "DbItem", "DesignDbItem", "LibraryDbItem",
    "Model"
]

from typing import Self, Optional

from PyQt6.QtCore import Qt, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtGui  import QStandardItemModel, QStandardItem

from . import logger, \
              LIB_EXT, DGM_EXT, DSN_EXT, \
              copy as master_copy, paste as master_paste, \
              fromXmlBegin, loadItems, saveBegin, saveEnd

from ..core    import toXmlAttrs, fromXmlAttrs

from .. import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..widgets import Drawing, Symbol, Diagram


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
    NAME = "Diagrams"
    BOLD   = False
    ITALIC = True

class SymbolCacheContainer(Container):
    NAME = "Symbol Cache"
    BOLD   = False
    ITALIC = True

class DesignDbContainer(Container):
    NAME = "Designs"
    BOLD   = True
    ITALIC = False

class DiagramDbContainer(Container):
    NAME = "Diagrams"
    BOLD   = True
    ITALIC = False

class LibraryDbContainer(Container):
    NAME = "Libraries"
    BOLD   = True
    ITALIC = False

class DrawingItem(QStandardItem):
    _scene_class = None

    @classmethod
    def sceneClass(cls):
        if cls._scene_class is None:
            from ..widgets.drawing.scenes import Drawing # deferred import
            cls._scene_class = Drawing
        return cls._scene_class

    scene : "Drawing"

    def __init__(self : Self, scene : Optional["Drawing"] = None) -> None:
        scene_class = self.__class__.sceneClass()
        self.scene = scene if scene else scene_class()
        super().__init__(self.scene.name)
        self.setData(self.scene, Qt.ItemDataRole.UserRole)
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsEditable)

    copy = master_copy

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self.scene.toXml(xw)

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        cls_name = cls.__name__.replace("Item", "")
        if xr.name() != cls_name:
            raise ValueError(f"Expected {cls_name} element, got {xr.name()}")
        scene_class = cls.sceneClass()
        scene = scene_class.fromXml(xr)
        instance : "DrawingItem" = cls(scene)
        return instance

class SymbolItem(DrawingItem):
    @classmethod
    def sceneClass(cls):
        if cls._scene_class is None:
            from ..widgets.drawing.scenes import Symbol # deferred import
            cls._scene_class = Symbol
        return cls._scene_class

    scene : "Symbol"

class DiagramItem(DrawingItem):
    @classmethod
    def sceneClass(cls):
        if cls._scene_class is None:
            from ..widgets.drawing.scenes import Diagram # deferred import
            cls._scene_class = Diagram
        return cls._scene_class

    scene : "Diagram"

class DbItem(QStandardItem):
    XML_ATTRS = {
        "name" : ("str", QStandardItem.setText, QStandardItem.text)
    }

    path : Optional[str]

    def __init__(self : Self) -> None:
        u = "Untitled" + self.__class__.__name__.replace("Item", "")
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
        if path is not None:
            self.path = path
        if self.path is None:
            self.path = self.saveAs()
        else:
            xw, file = saveBegin(self.path)
            self.toXml(xw)
            saveEnd(xw, file)

    copy = master_copy

class LibraryDbItem(DbItem):
    FILE_EXT = LIB_EXT

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self.toXmlBegin(xw)
        for i in range(self.rowCount()):
            symbol_item : SymbolItem = self.child(i)
            symbol_scene = symbol_item.scene
            symbol_scene.toXml(xw)
        self.toXmlEnd(xw)

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        db_item = cls.fromXmlBegin(xr)
        while not (xr.isEndElement() and xr.name() == cls.__name__.replace("Item", "")):
            xr.readNext()
        return db_item

class DiagramDbItem(DbItem):
    FILE_EXT = DGM_EXT

    diagram  : DiagramItem
    symbols  : SymbolCacheContainer

    def __init__(self : Self) -> None:
        super().__init__()
        self.diagram = DiagramItem()
        self.appendRow(self.diagram)
        self.symbols = SymbolCacheContainer()
        self.appendRow(self.symbols)

class DesignDbItem(DbItem):
    FILE_EXT = DSN_EXT

    diagrams : DiagramsContainer
    symbols  : SymbolCacheContainer

    def __init__(self : Self) -> None:
        super().__init__()
        self.diagrams = DiagramsContainer()
        self.appendRow(self.diagrams)
        self.symbols = SymbolCacheContainer()
        self.appendRow(self.symbols)

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
                                diagram_item = DiagramItem.fromXml(xr)
                                db_item.diagrams.appendRow(diagram_item)
                            else:
                                raise ValueError(f"Unexpected element in Diagrams: {xr.name()}")
                        xr.readNext()
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

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self.toXmlBegin(xw)
        xw.writeStartElement("Diagrams")
        for i in range(self.diagrams.rowCount()):
            diagram_item : DiagramItem = self.diagrams.child(i)
            diagram_scene = diagram_item.scene
            diagram_scene.toXml(xw)
        xw.writeEndElement()
        xw.writeStartElement("SymbolCache")
        for i in range(self.symbols.rowCount()):
            symbol_item : SymbolItem = self.symbols.child(i)
            symbol_scene = symbol_item.scene
            symbol_scene.toXml(xw)
        self.toXmlEnd(xw)

class Model(QStandardItemModel):
    def __init__(self : Self) -> None:
        super().__init__()
        self.setHorizontalHeaderLabels(["Database Hierarchy"])
        self.designs = DesignDbContainer()
        self.appendRow(self.designs)
        self.diagrams = DiagramDbContainer()
        self.appendRow(self.diagrams)
        self.libraries = LibraryDbContainer()
        self.appendRow(self.libraries)

    def newDesign(self : Self) -> DesignDbItem:
        item = DesignDbItem()
        self.designs.appendRow(item)
        return item

    def newDiagram(self : Self) -> DiagramDbItem:
        item = DiagramDbItem()
        self.diagrams.appendRow(item)
        return item

    def newLibrary(self : Self) -> LibraryDbItem:
        item = LibraryDbItem()
        self.libraries.appendRow(item)
        return item

    def newDiagram(
        self   : Self,
        parent : QStandardItem
    ) -> DiagramItem | None:
        item = None
        if isinstance(parent, DesignDbItem):
            parent = parent.diagrams
        if isinstance(parent, DiagramsContainer):
            item = DiagramItem()
            parent.appendRow(item)
        else:
            logger.warning(
                f"Unexpected parent item: {parent.text()} ({type(parent)})"
            )
        return item

    def newSymbol(
        self   : "Model",
        parent : QStandardItem
    ) -> SymbolItem | None:
        item = None
        if isinstance(parent, DesignDbItem):
            parent = parent.symbols
        if isinstance(parent, (SymbolCacheContainer, LibraryDbItem)):
            item = SymbolItem()
            parent.appendRow(item)
        else:
            logger.warning(
                f"Unexpected parent item: {parent.text()} ({type(parent)})"
            )
        return item

    def load(self : Self, path : str) -> DbItem:
        db_item = None
        if path.endswith(DSN_EXT):
            db_item = DesignDbItem.load(path)
            self.designs.appendRow(db_item)
        elif path.endswith(LIB_EXT):
            db_item = LibraryDbItem.load(path)
            self.libraries.appendRow(db_item)
        else:
            logger.warning(f"Unsupported file extension: {path}")
        return db_item

    def close(self : Self, item: QStandardItem) -> None:
        """Close a database and remove it from the model."""
        if isinstance(item, DesignDbItem):
            for i in range(self.designs.rowCount()):
                if item == self.designs.child(i):
                    self.designs.removeRow(i)
        elif isinstance(item, LibraryDbItem):
            for i in range(self.libraries.rowCount()):
                if item == self.libraries.child(i):
                    self.libraries.removeRow(i)
        else:
            logger.warning(f"Unsupported item: {item.text()} ({type(item)})")

    def copy(self : Self, item : QStandardItem) -> None:
        master_copy(item)

    def paste(self : Self, item : QStandardItem) -> None:
        paste_items = master_paste()
        if paste_items:
            match self.getItemDescription(item):
                case "Designs":
                    valid_item_type_names = ["DesignItem"]
                case "Libraries":
                    valid_item_type_names = ["LibraryItem"]
                case "Diagrams":
                    valid_item_type_names = ["DiagramItem"]
                case "Symbol Cache":
                    valid_item_type_names = ["SymbolItem"]
                case "Libraries":
                    valid_item_type_names = ["SymbolItem"]
                case _:
                    raise ValueError(
                        f"Cannot paste into item: {item.text()} ({type(item)})")
            invalid_item_type_names = []
            invalid_item_count = 0
            for paste_item in paste_items:
                paste_item_type_name = type(paste_item).__name__
                if paste_item_type_name not in valid_item_type_names:
                    invalid_item_type_names.append(paste_item_type_name)
                    invalid_item_count += 1
                else:
                    item.appendRow(paste_item)
                    # TODO: handle duplicate names
            if invalid_item_count:
                # TODO message box
                n = invalid_item_count
                s = ", ".join(invalid_item_type_names)
                raise ValueError(f"{n} invalid items for paste operation: {s}")

    def getDbItemFromScene(self : Self, scene : "Drawing") -> DbItem:
        for i in range(self.designs.rowCount()):
            db_item = self.designs.child(i)
            for j in range(db_item.diagrams.rowCount()):
                drawing_item : DrawingItem = db_item.diagrams.child(j)
                if scene == drawing_item.scene:
                    return db_item
            for j in range(db_item.symbols.rowCount()):
                drawing_item : DrawingItem = db_item.symbols.child(j)
                if scene == drawing_item.scene:
                    return db_item
        for i in range(self.libraries.rowCount()):
            db_item = self.libraries.child(i)
            for j in range(db_item.rowCount()):
                drawing_item : DrawingItem = db_item.child(j)
                if scene == drawing_item.scene:
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
