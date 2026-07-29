from __future__ import annotations

from typing import Self, cast

from PyQt6.QtCore import QSize, QXmlStreamWriter, QXmlStreamReader

from ..app import window

from ..resources import getIconPath

from ..core.check   import checked
from ..core.session import DocType, Session
from ..core.types   import MenuSub, MenuAction, MenuSeparator, MenuEntry
from ..core.doc     import NavItemSpec, DocSubjectProtocol, Doc
from ..core.icon    import SvgIconSingleton
from ..core.xml     import toXmlStartElement, toXmlEndElement, fromXml, loadXml
from ..core.utils   import space2underscore, cleanPath

from ..widgets.window.sub_window import DocSubWindow

from ..widgets.graphics.views.symbol import SymbolView
from ..widgets.graphics.views.block  import BlockView

from ..widgets.graphics.scenes.symbol import SymbolScene
from ..widgets.graphics.scenes.block  import BlockScene

from ..widgets.graphics.items.symbol import SymbolDefinitionItem
from ..widgets.graphics.items.block  import BlockDefinitionItem


class BaseIcon(SvgIconSingleton):
    SIZE = QSize(16, 16)


class LibraryIcon(BaseIcon):
    PATH = getIconPath("library.svg")


class SymbolIcon(BaseIcon):
    PATH = getIconPath("symbol.svg")


class BlockIcon(BaseIcon):
    PATH = getIconPath("block.svg")


DefinitionItem = SymbolDefinitionItem | BlockDefinitionItem
DefinitionScene = SymbolScene | BlockScene

class HdlSchematicLibraryDoc(Doc):
    _XML_TAG = "HdlSchematicLibrary"

    # instance attributes
    _name        : str
    _definitions : list[DefinitionItem]
    _scenes      : dict[DefinitionItem, DefinitionScene]
    _modified    : set[DefinitionItem]

    def __init__(self : Self, name : str | None = None) -> None:
        self._definitions = []
        self._scenes = {}
        self._modified = set()
        self.setName(name or "Untitled")

    # --- persistence (Session) ------------------------------------------------

    @checked
    def isClean(
        self    : Self,
        subject : DocSubjectProtocol
    ) -> bool:
        if subject is self:
            return all(
                scene.undo_stack.isClean()
                for scene in self._scenes.values()
            ) and len(self._modified) == 0
        if not isinstance(subject, DefinitionItem):
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
        for definition in self._definitions:
            definition.toXml(xw)
        toXmlEndElement(xw)

    @classmethod
    @checked
    def fromXml(
        cls : type[Self],
        xr  : QXmlStreamReader,
    ) -> Self:
        doc = cls()
        xref = {
            "Symbol" : lambda xr: SymbolDefinitionItem.fromXml(xr),
            "Block"  : lambda xr: BlockDefinitionItem.fromXml(xr)
        }
        fromXml(xr, xref, cls._XML_TAG)
        return doc

    @checked
    def save(self : Self, path : str | None = None) -> bool:
        # commit all modified scenes
        for defn, scene in self._scenes.items():
            if scene.undo_stack.isClean():
                continue
            if isinstance(defn, SymbolDefinitionItem) \
            and isinstance(scene, SymbolScene):
                defn.syncFromScene(scene)
            elif isinstance(defn, BlockDefinitionItem) \
            and isinstance(scene, BlockScene):
                defn.syncFromScene(scene)
            else:
                raise TypeError(
                    f"Mismatched definition/scene: {type(defn)} / {type(scene)}"
                )
            scene.undo_stack.setClean()
            self._modified.add(defn)
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
        children = []
        for definition in self._definitions:
            if isinstance(definition, SymbolDefinitionItem):
                icon = SymbolIcon().get()
            elif isinstance(definition, BlockDefinitionItem):
                icon = BlockIcon().get()
            else:
                raise RuntimeError(f"Unsupported definition type: {type(definition)}")
            children.append(NavItemSpec(subject = definition, icon = icon))
        return NavItemSpec(
            subject  = self,
            icon     = LibraryIcon().get(),
            tip      = self._path or "(not saved)",
            children = children
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
        if subject is self:
            self.setName(label)
        elif subject in self._definitions:
            subject.setName(label)
        else:
            raise RuntimeError("Bad subject")
        return True

    @checked
    def navDisplayLabel(
        self    : Self,
        subject : DocSubjectProtocol
    ) -> str:
        if subject is None:
            subject = self._scene
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
        if subject is self:
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
        if not isinstance(subject, DefinitionItem):
            raise RuntimeError("Bad subject")
        subwindows = window().mdiArea().docSubjectSubWindows(self, subject)
        menu_entries = []
        if len(subwindows) > 0:
            if not self._scenes[subject].undo_stack.isClean():
                menu_entries.extend([
                    MenuAction(
                        "Commit",
                        lambda s=subject: self.commit(subwindows[0])
                    ),
                    MenuSeparator(),
                ])
        menu_entries.append(
            MenuAction(
                "Edit",
                lambda s=subject: (self.showWindow(s), None)[1]
            )
        )
        if len(subwindows) > 0:
            menu_entries.append(
                MenuAction(
                    "New Window",
                    lambda s=subject: (self.newWindow(s), None)[1]
                )
            )
        menu_entries.extend([
            MenuSeparator(),
            MenuAction(
                "Duplicate",
                lambda s=subject: self.duplicateDefinitionHandler(s)
            ),
            MenuAction(
                "Delete",
                lambda s=subject: self.deleteDefinitionHandler(s),
                len(subwindows) == 0
            )
        ])
        return menu_entries

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
        if not isinstance(view, SymbolView | BlockView):
            raise RuntimeError("Bad view")
        scene = view.scene()
        if isinstance(subject, SymbolDefinitionItem):
            if not isinstance(scene, SymbolScene):
                raise RuntimeError("Bad scene")
            subject.syncFromScene(scene)
        elif isinstance(subject, BlockDefinitionItem):
            if not isinstance(scene, BlockScene):
                raise RuntimeError("Bad scene")
            subject.syncFromScene(scene)
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

    def duplicateDefinitionHandler(self : Self, subject : DefinitionItem) -> None:
        raise NotImplementedError("Not implemented")

    def deleteDefinitionHandler(self : Self, subject : DefinitionItem) -> None:
        raise NotImplementedError("Not implemented")


# register document type with Session

Session.registerDocType(DocType(
    name  = "HDL Schematic Library",
    group = "HDL Schematic Libraries",
    ext   = "hdl_lib",
    cls   = HdlSchematicLibraryDoc,
))
