from __future__ import annotations

from typing import Self, TypeAlias

from ....app import logger, session

from ....core.doc import Doc

from ...dialogs.file import FileNewDialog, FileOpenDialog, FileSaveAsDialog

from ..sub_window import DocSubWindow

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Navigator
    MixinSelf: TypeAlias = Self | Navigator
else:
    MixinSelf = Self


class NavigatorApiMixin:
    def docLoad(self : MixinSelf, path : str) -> None:
        """Load a file."""
        doc = session().load(path)
        if doc is None:
            return
        doc_type = session().docTypeForDoc(doc)
        if doc_type is None:
            return
        group_item = self._groups.get(doc_type.group, None)
        parent = self._model if group_item is None else group_item
        self._addDoc(parent, doc, path)

    def docSave(self : MixinSelf, doc : Doc) -> None:
        """Save a document."""
        session().save(doc)

    def docSaveAs(self : MixinSelf, doc : Doc, path : str) -> None:
        """Save a document as."""
        if session().saveAs(doc, path):
            doc.setPath(path)

    def docClose(self : MixinSelf, doc : Doc) -> None:
        """Close a document."""
        session().close(doc)

    def fileNew(self : MixinSelf) -> None:
        """Create a new document."""
        dialog = FileNewDialog(self)
        if not dialog.exec():
            return
        doc_type = dialog.docType()
        if doc_type is None:
            return
        doc = session().new(doc_type.tag)
        group_item = self._groups.get(doc_type.group, None)
        parent = self._model if group_item is None else group_item
        self._addDoc(parent, doc)

    def fileOpen(self : MixinSelf) -> None:
        """Open a document."""
        dialog = FileOpenDialog()
        if not dialog.exec():
            return
        files = dialog.selectedFiles()
        for file in files:
            self.docLoad(file)

    def fileSave(self : MixinSelf, subwindow : DocSubWindow) -> None:
        """Save a document."""
        doc = self._docFromSubwindow(subwindow)
        if doc is None:
            return
        self.docSave(doc)

    def fileSaveAs(
        self      : MixinSelf,
        subwindow : DocSubWindow,
        path      : str
    ) -> None:
        """Save a document as."""
        dialog = FileSaveAsDialog(subwindow.docBinding().doc.docType().tag)
        if not dialog.exec():
            return
        path = dialog.selectedFiles()[0]
        doc = self._docFromSubwindow(subwindow)
        if doc is None:
            logger().error("Subwindow has no document")
            return
        self.docSaveAs(doc, path)

    def fileClose(self : MixinSelf, subwindow : DocSubWindow) -> None:
        """Close a document."""
        doc = self._docFromSubwindow(subwindow)
        if doc is None:
            return
        self.docClose(doc)
        subwindow.close()

    def _docFromSubwindow(
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
