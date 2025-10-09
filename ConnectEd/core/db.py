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

    def root(self : Self) -> "DiagramItem":
        return self._root

    def setRoot(self : Self, item : "DiagramItem") -> None:
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
        return self.__class__.__name__.replace("Item", "")

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self._scene.toXml(xw)

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        scene : "DrawingScene" = cls.sceneClass().fromXml(xr)
        item : "DrawingItem" = cls(scene)
        return item

    copy = copy


class SymbolItem(DrawingItem):
    @classmethod
    def sceneClass(cls):
        from ..widgets.graphics.scenes.symbol import SymbolScene
        return SymbolScene

    _scene : "SymbolScene"

    def symbol(self : Self) -> "SymbolScene":
        return self._scene

    def dbItem(self : Self) -> "LibraryDbItem | DesignDbItem":
        """Symbols live in the Symbol Cache of a design, or in a library."""
        parent = self.parent()
        if isinstance(parent, SymbolCacheContainer):
            return parent.parent()
        else:
            return parent


class DiagramItem(DrawingItem):
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

    def dbItem(self : Self) -> "DesignDbItem":
        """
        For now, diagrams always live in a diagrams container under a design.
        """
        return self.parent().parent()


class DbItem(QStandardItem):
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
        return cls.__name__.replace("DbItem", "")

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


class DesignDbItem(DbItem):
    FILE_EXT = DSN_EXT

    _diagrams : DiagramsContainer
    _symbols  : SymbolCacheContainer

    def __init__(self : Self, name : str | None = None) -> None:
        super().__init__(name)
        self._diagrams = DiagramsContainer()
        self.appendRow(self._diagrams)
        self._symbols = SymbolCacheContainer()
        self.appendRow(self._symbols)
        if name is None:
            self._diagrams.appendRow(DiagramItem())
            self._diagrams.setRoot(self._diagrams.child(0))
        else:
            self._diagrams.setRoot(None)

    def diagramsItem(self : Self) -> DiagramsContainer:
        return self._diagrams

    def diagramItems(self : Self) -> list[DiagramItem]:
        return [self._diagrams.child(i) for i in range(self._diagrams.rowCount())]

    def rootDiagramItem(self : Self) -> DiagramItem | None:
        if self._diagrams.root() is None:
            return None
        return self._diagrams.root()

    def symbolsItem(self : Self) -> SymbolCacheContainer:
        return self._symbols

    def symbolItems(self : Self) -> list[SymbolItem]:
        return [self._symbols.child(i) for i in range(self._symbols.rowCount())]

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self.toXmlBegin(xw)
        xw.writeStartElement("Diagrams")
        root = "" if self._diagrams.root() is None \
            else self._diagrams.root().text()
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
        xw.writeEndElement()
        self.toXmlEnd(xw)

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        db_item : Self = cls.fromXmlBegin(xr)
        while not (xr.isEndElement() and xr.name() == cls.dbTypeName(cls)):
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
                                db_item._diagrams.appendRow(diagram_item)
                            else:
                                raise ValueError(f"Unexpected element in Diagrams: {xr.name()}")
                        xr.readNext()
                    # Set the root diagram based on the loaded name
                    if root_name:
                        root = None
                        for i in range(db_item._diagrams.rowCount()):
                            diagram_item = db_item._diagrams.child(i)
                            if diagram_item.text() == root_name:
                                root = diagram_item
                                db_item._diagrams.setRoot(root)
                                break
                        if root is None:
                            logger().warning(f"DesignDbItem.fromXml: Root diagram '{root_name}' not found, defaulting to first")
                            if db_item._diagrams.rowCount() > 0:
                                db_item._diagrams.setRoot(db_item._diagrams.child(0))
                    elif db_item._diagrams.rowCount() > 0:
                        db_item._diagrams.setRoot(db_item._diagrams.child(0))
                elif xr.name() == "SymbolCache":
                    xr.readNext()  # Move past <SymbolCache>
                    while not (xr.isEndElement() and xr.name() == "SymbolCache"):
                        if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                            if xr.name() == "Symbol":
                                symbol_item = SymbolItem.fromXml(xr)
                                db_item._symbols.appendRow(symbol_item)
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

    def newDesignItem(self : Self, name : str | None = None) -> DesignDbItem:
        item = DesignDbItem(name)
        self._designs.appendRow(item)
        return item

    def newLibraryItem(self : Self) -> LibraryDbItem:
        item = LibraryDbItem()
        self._libraries.appendRow(item)
        return item

    def newDiagramItem(
        self   : Self,
        parent : QStandardItem,
        name   : str | None = None
    ) -> DiagramItem | None:
        item = None
        if isinstance(parent, DesignDbItem):
            parent = parent._diagrams
        if isinstance(parent, DiagramsContainer):
            item = DiagramItem(name)
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

    def load(self : Self, path : str) -> DbItem | None:
        if self._alreadyLoaded(path):
            return None
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

    def close(self : Self, item : QStandardItem) -> None:
        from ..widgets.window.sub_window import SubWindow
        """Close a database and remove it from the model."""
        if isinstance(item, DesignDbItem):
            # close all open diagram windows for this design
            for i in range(item._diagrams.rowCount()):
                diagram_item = item._diagrams.child(i)
                if isinstance(diagram_item, DiagramItem):
                    for view in diagram_item.views():
                        if view:
                            subwindow : DrawingSubWindow | None = \
                                view.parentWidget()
                            if subwindow:
                                subwindow.close()
            # close all open symbol windows for this design
            for i in range(item._symbols.rowCount()):
                symbol_item = item._symbols.child(i)
                if isinstance(symbol_item, SymbolItem):
                    for view in symbol_item.views():
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
        elif isinstance(item, LibraryDbItem):
            # close all open symbol windows for this library
            for i in range(item.rowCount()):
                symbol_item = item.child(i)
                if isinstance(symbol_item, SymbolItem):
                    for view in symbol_item.views():
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

    def _alreadyLoaded(self : Self, path : str) -> bool:
        for i in range(self._designs.rowCount()):
            db_item : DesignDbItem = self._designs.child(i)
            if db_item._path == path:
                return True
        for i in range(self._libraries.rowCount()):
            db_item : LibraryDbItem = self._libraries.child(i)
            if db_item._path == path:
                return True
        return False
