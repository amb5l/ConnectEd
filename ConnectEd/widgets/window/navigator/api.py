from __future__ import annotations

from typing import Self, TypeAlias

from ....app import logger, session, settings

from ....core.session import DocType
from ....core.doc     import Doc
from ....core.utils   import cleanPath

from ...dialogs.file import FileNewDialog, FileOpenDialog, FileSaveAsDialog

from ..sub_window import DocSubWindow

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Navigator
    MixinSelf: TypeAlias = Self | Navigator
else:
    MixinSelf = Self


class NavigatorApiMixin:
    def docNew(self : MixinSelf, doc_type : DocType) -> None:
        """Create a new document."""
        doc = session().new(doc_type)
        group_item = self._group_items.get(doc_type.group, None)
        parent = self._model if group_item is None else group_item
        self._addDoc(parent, doc)

    def docNewPrompt(self : MixinSelf) -> None:
        """Create a new document."""
        dialog = FileNewDialog(self)
        if not dialog.exec():
            return
        doc_type = dialog.docType()
        if doc_type is None:
            return
        self.docNew(doc_type)

    def docLoad(self : MixinSelf, path : str) -> None:
        """Load a file."""
        path = cleanPath(path)
        doc = session().load(path)
        if doc is None:
            return
        settings().addMRU(path)
        doc_type = session().docTypeForDoc(doc)
        if doc_type is None:
            return
        group_item = self._group_items.get(doc_type.group, None)
        parent = self._model if group_item is None else group_item
        self._addDoc(parent, doc, path)

    def docSave(self : MixinSelf, doc : Doc) -> None:
        """Save a document."""
        session().save(doc)

    def docSaveAs(self : MixinSelf, doc : Doc, path : str) -> None:
        """Save a document as."""
        session().saveAs(doc, path)

    def docSaveAsPrompt(self : MixinSelf, doc : Doc) -> None:
        """Save a document as."""
        doc_type = session().docTypeForDoc(doc)
        if doc_type is None:
            return
        dialog = FileSaveAsDialog(doc_type, self)
        if not dialog.exec():
            return
        path = dialog.selectedFiles()[0]
        self.docSaveAs(doc, path)

    def docClose(self : MixinSelf, doc : Doc) -> None:
        """Close a document and its editors."""
        self._closeSubwindowsForDoc(doc)
        session().close(doc)

    def fileNew(self : MixinSelf) -> None:
        """Create a new document."""
        self.docNewPrompt()

    def fileOpen(
        self     : MixinSelf,
        doc_type : DocType | None = None,
    ) -> None:
        """Open a document."""
        dialog = FileOpenDialog(self, doc_type)
        if not dialog.exec():
            return
        files = dialog.selectedFiles()
        for file in files:
            self.docLoad(file)

    def fileSave(self : MixinSelf, subwindow : DocSubWindow) -> None:
        """Save a document."""
        doc = self._docFromSubWindow(subwindow)
        if doc is None:
            return
        if doc.path():
            self.docSave(doc)
        else:
            self.docSaveAsPrompt(doc)

    def fileSaveAs(
        self      : MixinSelf,
        subwindow : DocSubWindow,
        path      : str
    ) -> None:
        """Save a document as."""
        doc = self._docFromSubWindow(subwindow)
        if doc is None:
            logger().error("Subwindow has no document")
            return
        self.docSaveAsPrompt(doc)

    def fileClose(self : MixinSelf, subwindow : DocSubWindow) -> None:
        """Close an editor, or the whole document when appropriate."""
        doc = self._docFromSubWindow(subwindow)
        if doc is None:
            subwindow.close()
            return
        binding = subwindow.docBinding()
        if binding is None:
            subwindow.close()
            return
        if doc.isPrimarySubject(binding.subject) \
                or not self._subwindowsForDoc(doc, exclude=subwindow):
            self.docClose(doc)
        else:
            subwindow.close()

    def _docFromSubWindow(
        self      : MixinSelf,
        subwindow : DocSubWindow
    ) -> Doc | None:
        doc_binding = subwindow.docBinding()
        if doc_binding is None:
            logger().warning("Subwindow has no document binding")
            return None
        doc = doc_binding.doc
        if doc is None:
            return None
        return doc
