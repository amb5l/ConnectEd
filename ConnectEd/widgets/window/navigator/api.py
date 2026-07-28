from __future__ import annotations

from typing import Self

from ....app import logger, session, settings

from ....core.session import DocType
from ....core.doc     import Doc
from ....core.utils   import cleanPath

from ...dialogs.file import FileNewDialog, FileOpenDialog, FileSaveAsDialog

from ..sub_window import DocSubWindow


class NavigatorApiMixin:
    def docNew(self : Self, doc_type : DocType) -> None:
        """Create a new document."""
        from . import Navigator
        if not isinstance(self, Navigator): raise TypeError("Bad host")
        doc = session().new(doc_type)
        group_item = self._group_items.get(doc_type.group, None)
        parent = self._model if group_item is None else group_item
        self._addDoc(parent, doc)

    def docNewPrompt(self : Self) -> None:
        """Create a new document."""
        from . import Navigator
        if not isinstance(self, Navigator): raise TypeError("Bad host")
        dialog = FileNewDialog(self)
        if not dialog.exec():
            return
        if (doc_type := dialog.docType()) is None:
            return
        self.docNew(doc_type)

    def docLoad(self : Self, path : str) -> None:
        """Load a file."""
        from . import Navigator
        if not isinstance(self, Navigator): raise TypeError("Bad host")
        path = cleanPath(path)
        if (doc := session().load(path)) is None:
            return
        settings().addMRU(path)
        if (doc_type := session().docTypeForDoc(doc)) is None:
            return
        group_item = self._group_items.get(doc_type.group, None)
        parent = self._model if group_item is None else group_item
        self._addDoc(parent, doc, path)

    def docSave(self : Self, doc : Doc) -> None:
        """Save a document."""
        session().save(doc)

    def docSaveAs(self : Self, doc : Doc, path : str) -> None:
        """Save a document as."""
        session().saveAs(doc, path)

    def docSaveAsPrompt(self : Self, doc : Doc) -> None:
        """Save a document as."""
        from . import Navigator
        if not isinstance(self, Navigator): raise TypeError("Bad host")
        if (doc_type := session().docTypeForDoc(doc)) is None:
            return
        dialog = FileSaveAsDialog(doc_type, self)
        if not dialog.exec():
            return
        path = dialog.selectedFiles()[0]
        self.docSaveAs(doc, path)

    def docClose(self : Self, doc : Doc) -> None:
        """Close a document and its editors."""
        from . import Navigator
        if not isinstance(self, Navigator): raise TypeError("Bad host")
        self._closeSubwindowsForDoc(doc)
        session().close(doc)

    def fileNew(self : Self) -> None:
        """Create a new document."""
        self.docNewPrompt()

    def fileOpen(
        self     : Self,
        doc_type : DocType | None = None,
    ) -> None:
        """Open a document."""
        from . import Navigator
        if not isinstance(self, Navigator): raise TypeError("Bad host")
        dialog = FileOpenDialog(self, doc_type)
        if not dialog.exec():
            return
        files = dialog.selectedFiles()
        for file in files:
            self.docLoad(file)

    def fileSave(self : Self, subwindow : DocSubWindow) -> None:
        """Save a document."""
        from . import Navigator
        if not isinstance(self, Navigator): raise TypeError("Bad host")
        if (doc := self._docFromSubWindow(subwindow)) is None:
            return
        if doc.path():
            self.docSave(doc)
        else:
            self.docSaveAsPrompt(doc)

    def fileSaveAs(
        self      : Self,
        subwindow : DocSubWindow
    ) -> None:
        """Save a document as."""
        if (doc := self._docFromSubWindow(subwindow)) is None:
            logger().error("Subwindow has no document")
            return
        self.docSaveAsPrompt(doc)

    def fileClose(self : Self, subwindow : DocSubWindow) -> None:
        """Close an editor, or the whole document when appropriate."""
        from . import Navigator
        if not isinstance(self, Navigator): raise TypeError("Bad host")
        if (doc := self._docFromSubWindow(subwindow)) is None:
            subwindow.close()
            return
        if (binding := subwindow.docBinding()) is None:
            subwindow.close()
            return
        if doc.isPrimarySubject(binding.subject) \
                or not self._subwindowsForDoc(doc, exclude=subwindow):
            self.docClose(doc)
        else:
            subwindow.close()

    def editCopy(self : Self) -> None:
        raise NotImplementedError("Not implemented")

    def editPaste(self : Self) -> None:
        raise NotImplementedError("Not implemented")

    def _docFromSubWindow(
        self      : Self,
        subwindow : DocSubWindow
    ) -> Doc | None:
        if (doc_binding := subwindow.docBinding()) is None:
            logger().warning("Subwindow has no document binding")
            return None
        return doc_binding.doc
