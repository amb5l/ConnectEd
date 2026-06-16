from typing      import Self, ClassVar
from dataclasses import dataclass

from PyQt6.QtCore import QObject, pyqtSignal, \
                         QFile, QIODevice, QXmlStreamReader

from ..app import logger

from .check import checked
from .defs  import APP_NAME
from .doc   import Doc


@dataclass
class DocType:
    """A document type."""
    name  : str        # friendly document type name
    group : str        # friendly document group name
    ext   : str        # file extension
    tag   : str        # XML tag
    cls   : type[Doc]  # class to instantiate


class Session(QObject):
    """
    Application session manager. Open diagrams, libraries etc live here.
    """

    _doc_types : ClassVar[dict[str, DocType]] = {}
    _open_docs : list[Doc]

    docChanged = pyqtSignal(Doc)  # noqa N815

    def __init__(self):
        self._open_docs = []

    def onDocChanged(self : Self, doc : Doc) -> None:
        self.docChanged.emit(doc)

    @checked
    def new(self : Self, tag : str) -> Doc | None:
        """Create a new document."""
        doc_type = self.docTypeForTag(tag)
        if doc_type is None:
            logger().error(f"Unknown document tag {tag!r}")
            return None
        doc = doc_type.cls()
        self._open_docs.append(doc)
        return doc

    @checked
    def load(self, path : str) -> Doc | None:
        # check if already open
        existing_doc = self.openDocForPath(path)
        if existing_doc is not None:
            return existing_doc
        # open file
        file = QFile(path)
        if not file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
            logger().error(f"Failed to open: {path}")
            return None
        # stream XML from file
        xr = QXmlStreamReader(file)
        try:
            # find app element
            while not xr.atEnd():
                if xr.isStartElement() and xr.name() == APP_NAME:
                    break
                xr.readNext()
            else:
                logger().error(f"No {APP_NAME} root element in {path}")
                return None
            # find document element
            while not xr.atEnd():
                xr.readNext()
                if xr.isEndElement() and xr.name() == APP_NAME:
                    logger().error(f"No document element in {path}")
                    return None
                if not xr.isStartElement():
                    continue
                tag = xr.name()
                doc_type = self.docTypeForTag(tag)
                if doc_type is None:
                    logger().error(f"Unknown document tag {tag!r} in {path}")
                    return None
                try:
                    doc = doc_type.cls.fromXml(xr)
                except Exception as e:
                    logger().error(f"Failed to load {path}: {e}")
                    return None
                self._open_docs.append(doc)
                return doc
        finally:
            file.close()
        return None

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

    def saveAs(self : Self, doc : Doc, path : str) -> None:
        """Save a document."""
        for open_doc in self._open_docs:
            if open_doc == doc:
                doc.save(path)
                return
        logger().warning(f"Document not found: {doc}")

    def close(self : Self, doc : Doc) -> None:
        """Close a document."""
        for open_doc in self._open_docs:
            if open_doc == doc:
                self._open_docs.remove(open_doc)
                return
        logger().warning(f"Document not found: {doc}")

    @classmethod
    def registerDocType(
        cls,
        name    : str,
        group   : str,
        ext     : str,
        tag     : str,
        doc_cls : type[Doc],
    ) -> None:
        if tag in cls._doc_types:
            logger().warning(
                f"Document tag {tag!r} already registered "
                f"as {cls._doc_types[tag].name!r}"
            )
            return
        cls._doc_types[tag] = DocType(name, group, ext, tag, doc_cls)

    def docTypes(self : Self) -> list[DocType]:
        """List of document types."""
        return list(self._doc_types.values())

    def docTypeForDoc(self : Self, doc : Doc) -> DocType | None:
        for doc_type in self._doc_types.values():
            if doc_type.cls == doc.__class__:
                return doc_type
        return None

    def docTypeForExt(self : Self, ext : str) -> DocType | None:
        for doc_type in self._doc_types.values():
            if doc_type.ext == ext:
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
