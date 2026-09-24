from __future__ import annotations

from typing import Self, cast

from PyQt6.QtCore import QSize, QXmlStreamWriter, QXmlStreamReader

from ....app import window

from ....resources import getIconPath

from ....core.check   import checked
from ....core.session import DocType, Session
from ....core.types   import MenuSub, MenuAction, MenuSeparator, MenuEntry
from ....core.doc     import NavItemSpec, DocSubjectProtocol, Doc, DocBinding
from ....core.icon    import SvgIconSingleton
from ....core.xml     import toXmlStartElement, toXmlEndElement, fromXml, loadXml
from ....core.utils   import space2underscore, cleanPath

from ....widgets.dialogs.unsaved_changes import UnsavedChangesDialog

from ....widgets.window.sub_window import DocSubWindow

from ....widgets.graphics.views.symbol import SymbolView

from ....widgets.graphics.scenes.symbol import SymbolScene

from ....widgets.graphics.items.symbol import SymbolDefinitionItem

from ....widgets.library.sub_window import LibrarySubWindow

from ....domains.hdl.schematic.library import HdlSchematicLibrary


class BaseIcon(SvgIconSingleton):
    SIZE = QSize(16, 16)


class LibraryIcon(BaseIcon):
    PATH = getIconPath("library.svg")


class SymbolIcon(BaseIcon):
    PATH = getIconPath("symbol.svg")


class BlockIcon(BaseIcon):
    PATH = getIconPath("block.svg")


class HdlSchematicLibraryDoc(Doc[HdlSchematicLibrary]):
    _XML_TAG = "HdlSchematicLibrary"

    # instance attributes
    _scenes   : dict[SymbolDefinitionItem, SymbolScene]
    _modified : set[SymbolDefinitionItem]

    def __init__(self : Self, name : str | None = None) -> None:
        self._path     = ""
        self._object   = HdlSchematicLibrary()
        self._scenes   = {}
        self._modified = set()
        self.setName(name or "Untitled")

    # --- persistence (Session) ------------------------------------------------

    @checked
    def isClean(
        self    : Self,
        subject : DocSubjectProtocol
    ) -> bool:
        if subject is self._object:
            return all(
                scene.undo_stack.isClean()
                for scene in self._scenes.values()
            ) and len(self._modified) == 0
        if not isinstance(subject, SymbolDefinitionItem):
            raise RuntimeError("Bad subject")
        clean = True
        clean = subject.name() not in self._modified
        if subject in self._scenes.keys():
            clean = clean and self._scenes[subject].undo_stack.isClean()
        return clean

    @checked
    def name(self : Self) -> str:
        return self._name

    @checked
    def setName(self : Self, name : str) -> None:
        self._name = name
        self.onChanged()

    @checked
    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        toXmlStartElement(xw, self._XML_TAG)
        xw.writeAttribute(space2underscore("name"), self._name)
        for symbol in self._object.getSymbols().values():
            symbol.toXml(xw)
        toXmlEndElement(xw)

    @classmethod
    @checked
    def fromXml(
        cls : type[Self],
        xr  : QXmlStreamReader,
    ) -> Self:
        doc = cls()
        xref = {
            "Symbol" : lambda xr: SymbolDefinitionItem.fromXml(xr)
        }
        fromXml(xr, xref, cls._XML_TAG)
        return doc

    @checked
    def save(self : Self, path : str | None = None) -> bool:
        # commit all modified scenes
        for symbol, scene in self._scenes.items():
            if scene.undo_stack.isClean():
                continue
            item = scene.symbol()
            if item is None:
                raise RuntimeError("Scene has no item")
            symbol.syncFromDefinition(item)
            scene.undo_stack.setClean()
            self._modified.add(symbol)
        # attempt to save
        result = super().save(path)
        if result:
            self._modified.clear()
        return result

    @classmethod
    @checked
    def load(cls : type[Self], path : str) -> Self | None:
        return cast(Self, loadXml(cleanPath(path), {cls.tag(): cls}))

    # --- Navigator (tree presentation) ----------------------------------------

    @checked
    def navItemSpec(self : Self) -> NavItemSpec:
        return NavItemSpec(
            subject  = self._object,
            icon     = LibraryIcon().get(),
            tip      = self._path or "(not saved)",
            children = [
                NavItemSpec(subject = s, icon = SymbolIcon().get())
                for s in self._object.getSymbols().values()
            ]
        )

    @checked
    def navLabel(
        self    : Self,
        subject : DocSubjectProtocol
    ) -> str:
        return subject.name()

    @checked
    def navSetLabel(
        self    : Self,
        subject : DocSubjectProtocol,
        label   : str,
    ) -> bool:
        subject.setName(label)
        return True

    @checked
    def navDisplayLabel(
        self    : Self,
        subject : DocSubjectProtocol
    ) -> str:
        return subject.name() + ("" if self.isClean(subject) else "*")

    @checked
    def navToolTip(
        self    : Self,
        subject : DocSubjectProtocol
    ) -> str | None:
        return self._path or "(not saved)" if subject is self else None

    @checked
    def navContextMenu(
        self    : Self,
        subject : DocSubjectProtocol
    ) -> list[MenuEntry]:
        if subject is self._object:
            nav = window().navigator()
            return list[MenuEntry]([
                MenuSub("New", [
                    MenuAction("Symbol", lambda: self.newSymbolHandler()),
                    MenuAction("Block", lambda: self.newBlockHandler()),
                ]),
                MenuSeparator(),
                MenuAction("Save", lambda: nav.docSave(self)),
                MenuAction("Save As...", lambda: nav.docSaveAsPrompt(self)),
                MenuAction("Close", lambda: nav.docClose(self)),
            ])
        elif isinstance(subject, SymbolDefinitionItem) \
        and subject in self._object.getSymbols().values():
            subwindows = window().mdiArea().docSubjectSubWindows(self, subject)
            entries = []
            if len(subwindows) > 0:
                if not self._scenes[subject].undo_stack.isClean():
                    entries.extend([
                        MenuAction(
                            "Commit",
                            lambda s=subject: self.commit(subwindows[0])
                        ),
                        MenuSeparator(),
                    ])
            entries.append(
                MenuAction(
                    "Edit",
                    lambda s=subject: (self.showWindow(s), None)[1]
                )
            )
            if len(subwindows) > 0:
                entries.append(
                    MenuAction(
                        "New Window",
                        lambda s=subject: (self.newWindow(s), None)[1]
                    )
                )
            entries.extend([
                MenuSeparator(),
                MenuAction(
                    "Duplicate",
                    lambda s=subject: self.duplicateSymbolHandler(s)
                ),
                MenuAction(
                    "Delete",
                    lambda s=subject: self.deleteSymbolHandler(s),
                    len(subwindows) == 0
                )
            ])
            return entries
        else:
            raise RuntimeError("Bad subject")

    # --- MDI (subwindows) -----------------------------------------------------

    @checked
    def showWindow(self : Self, subject : DocSubjectProtocol) -> bool:
        """
        Show existing primary editing subwindow for subject, or creates a new
        one if none exists. Ignores auxilliary editors (spreadsheets etc).
        """
        subwindows = window().mdiArea().docSubjectSubWindows(self, subject)
        if subject is self._object:
            for subwindow in subwindows:
                if isinstance(subwindow, LibrarySubWindow):
                    window().mdiArea().activateSubWindow(subwindow)
                    return True
            else:
                return self.newWindow(subject)
        elif subject in self._object.getSymbols().values():
            from ....widgets.graphics.views.diagram import DiagramSubWindow
            from ....widgets.graphics.views.symbol  import SymbolSubWindow
            for subwindow in subwindows:
                if isinstance(subwindow, DiagramSubWindow | SymbolSubWindow):
                    window().mdiArea().activateSubWindow(subwindow)
                    return True
            else:
                return self.newWindow(subject)
        else:
            raise RuntimeError("Bad subject")

    @checked
    def newWindow(self : Self, subject : DocSubjectProtocol) -> bool:
        if (subwindow := self._createSubWindow(subject)) is None:
            return False
        subwindow.showMaximized()
        window().mdiArea().activateSubWindow(subwindow)
        return True

    @checked
    def windowTitle(self : Self, subject : DocSubjectProtocol) -> str:
        if subject is self._object:
            return self._object.name() + " - HDL Schematic Library"
        if subject in self._object.getSymbols().values():
            name = "Symbol" if isinstance(subject, SymbolDefinitionItem) else "Block"
            return subject.name() + f" - HDL Schematic Library {name}"
        return "Unknown Subject"

    @checked
    def mayCloseSubWindow(self : Self, subwindow : DocSubWindow) -> bool:
        """Prompt for commit/discard, and veto if necessary."""
        from ....widgets.graphics.items.symbol   import SymbolDefinitionItem
        # get subject
        subject = self._subjectFromSubwindow(subwindow)
        # prompt to save/commit when last window is closed
        if subject is self._object:
            return True
        elif isinstance(subject, SymbolDefinitionItem):
            # symbol
            if self._isSymbolClean(subject):
                return True
            subwindows = window().mdiArea().docSubjectSubWindows(self, subject)
            if len(subwindows) == 1:
                dialog = UnsavedChangesDialog(
                    f"Symbol '{subject.name()}' has been modified.",
                    window()
                )
                if dialog.exec():
                    if dialog.commit():
                        self.commit(subwindow)
                    scene = self._scenes[subject]
                    scene.undo_stack.setClean()
                    return True
                else:
                    return False
            return True
        return False

    @checked
    def onSubWindowClosed(self : Self, subwindow : DocSubWindow) -> None:
        # get subject
        subject = self._subjectFromSubwindow(subwindow)
        if subject is None: return
        # clean up _scenes, update _modified
        subwindows = window().mdiArea().docSubjectSubWindows(self, subject)
        if len(subwindows) == 1:
                if isinstance(subject, SymbolDefinitionItem) \
                and subject in self._scenes:
                    scene = self._scenes[subject]
                    if not scene.undo_stack.isClean():
                        self._modified.add(subject)
                    del self._scenes[subject]
        # clean up display labels
        window().mdiArea().onSubWindowsChanged()

    # --- editor lifecycle (close / save) --------------------------------------

    @checked
    def commit(self : Self, subwindow : DocSubWindow) -> None:
        binding = subwindow.docBinding()
        if binding is None:
            raise RuntimeError("No binding")
        if binding.doc is not self:
            raise RuntimeError("Bad binding")
        subject = binding.subject
        view = subwindow.widget()
        if not isinstance(view, SymbolView):
            raise RuntimeError("Bad view")
        scene = view.scene()
        if isinstance(subject, SymbolDefinitionItem):
            if not isinstance(scene, SymbolScene):
                raise RuntimeError("Bad scene")
            item = scene.symbol()
            if item is None:
                raise RuntimeError("Scene has no item")
            subject.syncFromDefinition(item)
        else:
            raise RuntimeError("Bad subject")
        scene.undo_stack.setClean()
        self._modified.add(subject)

    @checked
    def isPrimarySubject(self : Self, subject : DocSubjectProtocol) -> bool:
        return subject is self

    # --- menu action handlers -------------------------------------------------

    def newSymbolHandler(self : Self) -> None:
        raise NotImplementedError("Not implemented")

    def newBlockHandler(self : Self) -> None:
        raise NotImplementedError("Not implemented")

    def duplicateSymbolHandler(self : Self, subject : SymbolDefinitionItem) -> None:
        raise NotImplementedError("Not implemented")

    def deleteSymbolHandler(self : Self, subject : SymbolDefinitionItem) -> None:
        raise NotImplementedError("Not implemented")

    # --- helpers --------------------------------------------------------------

    def _createSubWindow(
        self    : Self,
        subject : DocSubjectProtocol,
    ) -> DocSubWindow | None:
        from ....widgets.graphics.views.symbol  import SymbolView, SymbolSubWindow
        from ....widgets.graphics.scenes.symbol import SymbolScene
        from ....widgets.graphics.items.symbol  import SymbolDefinitionItem
        binding = DocBinding(self, subject)
        mdi_area = window().mdiArea()
        if subject is self._object:
            from ....widgets.library.browser import LibraryBrowser
            from ....widgets.library.sub_window import LibrarySubWindow
            subwindow = LibrarySubWindow(mdi_area, binding)
            widget = LibraryBrowser(self._object)
        elif isinstance(subject, SymbolDefinitionItem) \
        and subject in self._object.getSymbols().values():
            if subject in self._scenes:
                scene = self._scenes[subject]
            else:
                scene = SymbolScene(subject.clone())
                scene.undo_stack.setClean()
                scene.undo_stack.cleanChanged.connect(
                    lambda clean, s=subject: self._onCleanChanged(s, clean)
                )
                self._scenes[subject] = scene
            subwindow = SymbolSubWindow(mdi_area, binding)
            widget = SymbolView(scene)
        else:
            raise RuntimeError("Bad subject")
        subwindow.setWidget(widget)
        mdi_area.addSubWindow(subwindow)
        return subwindow

    def _isSymbolClean(self : Self, subject : DocSubjectProtocol) -> bool:
        from ....widgets.graphics.items.symbol import SymbolDefinitionItem
        if not isinstance(subject, SymbolDefinitionItem):
            raise TypeError("Bad subject")
        if subject in self._scenes:
            return self._scenes[subject].undo_stack.isClean()
        return subject not in self._modified

    def _onCleanChanged(
        self    : Self,
        subject : DocSubjectProtocol,
        clean   : bool
    ) -> None:
        from ....widgets.graphics.items.symbol import SymbolDefinitionItem
        if not isinstance(subject, SymbolDefinitionItem):
            raise TypeError("Bad subject")
        if not clean:
            if subject not in self._modified:
                self._modified.add(subject)
        else:
            if subject in self._modified:
                self._modified.remove(subject)
        self.onChanged()


# register document type with Session

Session.registerDocType(DocType(
    name  = "HDL Schematic Library",
    group = "HDL Schematic Libraries",
    ext   = "lib.hdl",
    cls   = HdlSchematicLibraryDoc,
))
