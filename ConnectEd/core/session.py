import re

from typing      import Self, ClassVar, cast
from dataclasses import dataclass

from PyQt6.QtCore import QObject, pyqtSignal

from ..app import logger

from .check import checked
from .defs  import APP_EXT
from .doc   import Doc
from .utils import cleanPath
from .xml   import loadXml


@dataclass
class DocType:
    """A document type."""
    name  : str        # friendly document type name
    group : str        # friendly document group name
    ext   : str        # extension suffix, e.g. ``hdl_sch``
    cls   : type[Doc]  # class to instantiate

    @property
    def tag(self : Self) -> str:
        return self.cls.tag()

    @property
    def fileExt(self : Self) -> str:
        return f"{APP_EXT}_{self.ext}"


class Session(QObject):
    """
    Application session manager. Open diagrams, libraries etc live here.
    """

    _doc_types : ClassVar[dict[str, DocType]] = {}
    _open_docs : list[Doc]

    docChanged = pyqtSignal(Doc)  # noqa N815
    docClosed  = pyqtSignal(Doc)  # noqa N815

    def __init__(self):
        super().__init__()
        self._open_docs = []

    def onDocChanged(self : Self, doc : Doc) -> None:
        self.docChanged.emit(doc)

    @checked
    def new(self : Self, doc_type : DocType) -> Doc:
        """Create a new document."""
        # generate a unique "Untitled<number>" name
        peer_docs = [
            open_doc for open_doc in self._open_docs
            if open_doc.__class__ == doc_type.cls
        ]
        number = 1
        if peer_docs:
            for peer_doc in peer_docs:
                # regex match for "Untitled<number>"
                match = re.match(r"Untitled(\d+)", peer_doc.name())
                if match:
                    number = max(number, int(match.group(1)) + 1)
        name = f"Untitled{number}"
        doc = doc_type.cls()
        doc.setName(name)
        self._open_docs.append(doc)
        return doc

    @checked
    def load(self, path : str) -> Doc | None:
        if (existing_doc := self.openDocForPath(path)) is not None:
            return existing_doc
        path = cleanPath(path)
        elements = {
            doc_type.tag : doc_type.cls
            for doc_type in self._doc_types.values()
        }
        if (doc := loadXml(path, elements)) is None:
            return None
        self._open_docs.append(cast(Doc, doc))
        return cast(Doc, doc)

    def save(self : Self, doc : Doc) -> None:
        """Save a document."""
        for open_doc in self._open_docs:
            if open_doc == doc:
                if doc.path() == "":
                    logger().warning(f"Document has no path: {doc}")
                else:
                    doc.save()
                return
        logger().warning(f"Document not found: {doc}")

    def saveAs(self : Self, doc : Doc, path : str) -> bool:
        """Save a document."""
        for open_doc in self._open_docs:
            if open_doc == doc:
                return doc.save(path)
        logger().warning(f"Document not found: {doc}")
        return False

    def close(self : Self, doc : Doc) -> None:
        """Close a document."""
        for open_doc in self._open_docs:
            if open_doc == doc:
                self._open_docs.remove(open_doc)
                self.docClosed.emit(doc)
                return
        logger().warning(f"Document not found: {doc}")

    @classmethod
    def registerDocType(
        cls,
        doc_type : DocType,
    ) -> None:
        doc_cls = doc_type.cls
        tag = doc_cls.tag()
        if tag in cls._doc_types:
            logger().warning(
                f"Document tag {tag!r} already registered "
                f"as {cls._doc_types[tag].name!r}"
            )
            return
        cls._doc_types[tag] = doc_type

    def docTypes(self : Self) -> list[DocType]:
        """List of document types."""
        return list(self._doc_types.values())

    def docTypeForDoc(self : Self, doc : Doc) -> DocType | None:
        for doc_type in self._doc_types.values():
            if doc_type.cls == doc.__class__:
                return doc_type
        return None

    def docTypeForExt(self : Self, ext : str) -> DocType | None:
        if not ext.startswith("."):
            ext = f".{ext}"
        for doc_type in self._doc_types.values():
            if doc_type.fileExt == ext:
                return doc_type
        return None

    def docTypeForTag(self : Self, tag : str) -> DocType | None:
        return self._doc_types.get(tag)

    def openDocs(self : Self) -> list[Doc]:
        """List of open documents."""
        return self._open_docs

    def openDocForPath(self : Self, path : str) -> Doc | None:
        """Get document for a path, if already open."""
        for open_doc in self._open_docs:
            # how to we compare paths? normalise, surely.. remove dup slashes...
            if open_doc.path() == path:
                return open_doc
        return None

    @checked
    def fileFilters(
        self     : Self,
        doc_type : DocType | None = None,
    ) -> list[str]:
        """``QFileDialog`` name filters for open."""
        if doc_type is not None:
            return [f"{doc_type.name} (*{doc_type.fileExt})"]
        filters = [f"ConnectEd Documents (*{APP_EXT}*)"]
        for registered in self.docTypes():
            filters.append(f"{registered.name} (*{registered.fileExt})")
        filters.append("All Files (*.*)")
        return filters
