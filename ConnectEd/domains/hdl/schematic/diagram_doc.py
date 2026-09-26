#Priority	Issue
#P0: Store scene in registry (or drop _symbol_scenes and use **_dirty only consistently)
#P0: isClean(L2) aggregate includes dirty symbols
 #P0: Navigator navDisplayLabel on refresh
#P1: destroyed cleanup for symbol editors
 #P1: Diagram cleanChanged → onChanged()
#P1: Multiple editors: don’t clear _dirty while another stack is dirty
#P2: save() return value; setClean on all open symbol stacks
#P2: navToolTip modified suffix

from __future__ import annotations

from typing import Self, cast

from PyQt6.QtCore    import QSize, QXmlStreamWriter, QXmlStreamReader

from ....app       import logger, window
from ....resources import getIconPath

from ....core.check   import checked
from ....core.session import DocType, Session
from ....core.types   import MenuAction, MenuSeparator, MenuEntry
from ....core.doc     import NavItemSpec, DocSubjectProtocol, Doc, DocBinding
from ....core.icon    import SvgIconSingleton
from ....core.xml     import loadXml
from ....core.utils   import cleanPath

from ....widgets.dialogs.unsaved_changes import UnsavedChangesDialog

from ....widgets.graphics.scenes.diagram import DiagramScene
from ....widgets.graphics.items.symbol   import SymbolDefinitionItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....widgets.window.sub_window      import DocSubWindow
    from ....widgets.graphics.scenes.symbol import SymbolScene


class SchematicIcon(SvgIconSingleton):
    PATH = getIconPath("schematic.svg")
    SIZE = QSize(16, 16)


class SymbolIcon(SvgIconSingleton):
    PATH = getIconPath("symbol.svg")
    SIZE = QSize(16, 16)


class HdlSchematicDiagramDoc(Doc[DiagramScene]):
    _XML_TAG = "HdlSchematicDiagram"

    _scenes   : dict[SymbolDefinitionItem, SymbolScene]
    _modified : list[SymbolDefinitionItem]

    @checked
    def __init__(self : Self, name : str | None = None) -> None:
        from ....widgets.graphics.scenes.diagram import DiagramScene
        self._path = ""
        self._object = DiagramScene(self)
        self._scenes = {}
        self._modified = []
        self.setName(name or "Untitled")
        undo_stack = self._object.undo_stack
        undo_stack.setClean()
        undo_stack.cleanChanged.connect(
            lambda clean: self._onCleanChanged(self._object, clean)
        )

    # --- persistence (Session) ------------------------------------------------

    @checked
    def isClean(
        self    : Self,
        subject : DocSubjectProtocol
    ) -> bool:
        if subject is self._object:
            return self._object.undo_stack.isClean() \
                and self._modifiedSymbolsCount() == 0
        elif isinstance(subject, SymbolDefinitionItem):
            if subject in self._scenes:
                return self._scenes[subject].undo_stack.isClean()
            else:
                return subject in self._modified
        else:
            raise RuntimeError("Bad subject")

    @checked
    def name(self : Self) -> str:
        return self._object.name()

    @checked
    def setName(self : Self, name : str) -> None:
        self._object.setName(name)

    @checked
    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self._object.toXml(xw)

    @classmethod
    @checked
    def fromXml(
        cls : type[Self],
        xr  : QXmlStreamReader,
    ) -> Self:
        from ....widgets.graphics.scenes.diagram import DiagramScene
        doc = cls()
        scene = DiagramScene.fromXml(xr)
        scene._doc = doc
        doc._object = scene
        return doc

    @checked
    def save(self : Self, path : str | None = None) -> bool:
        self._object.undo_stack.setClean()
        self._modified = []
        return super().save(path)

    @classmethod
    @checked
    def load(cls : type[Self], path : str) -> Self | None:
        return cast(Self, loadXml(cleanPath(path), {cls.tag(): cls}))

    # --- Navigator (tree presentation) ----------------------------------------

    @checked
    def navItemSpec(self : Self) -> NavItemSpec:
        return NavItemSpec(
            subject  = self._object,
            icon     = SchematicIcon().get(),  # TODO remove this
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
        changed = False
        if label != subject.name():
            if subject is self._object:
                self._object.setName(label, notify=False)
                changed = True
            elif isinstance(subject, SymbolDefinitionItem) \
            and subject in self._object.getSymbols().values():
                self._object.renSymbol(subject, label)
                changed = True
        # update window titles and menu if any windows are open
        if window().mdiArea().docSubjectSubWindows(self, subject):
            window().mdiArea().onSubWindowsChanged()
        # done
        return changed

    @checked
    def navDisplayLabel(
        self    : Self,
        subject : DocSubjectProtocol,
    ) -> str:
        return subject.name() + ("" if self.isClean(subject) else "*")

    @checked
    def navToolTip(
        self    : Self,
        subject : DocSubjectProtocol | None = None
    ) -> str | None:
        return self._path or "(not saved)" if subject is self._object else None

    @checked
    def navContextMenu(
        self    : Self,
        subject : DocSubjectProtocol
    ) -> list[MenuEntry]:
        if subject is self._object:
            nav = window().navigator()
            entries : list[MenuEntry] = []
            entries = [
                MenuAction("Save", lambda: nav.docSave(self)),
                MenuAction("Save As...", lambda: nav.docSaveAsPrompt(self)),
                MenuAction("Close", lambda: nav.docClose(self)),
                MenuSeparator(),
                MenuAction(
                    "Edit",
                    lambda s=subject: (self.showWindow(s), None)[1]
                ),
            ]
            subwindows = window().mdiArea().docSubjectSubWindows(self, subject)
            if len(subwindows) > 0:
                entries.append(MenuAction(
                    "New Window",
                    lambda s=subject: (self.newWindow(s), None)[1]
                ))
            return entries
        elif isinstance(subject, SymbolDefinitionItem) \
        and subject in self._object.getSymbols().values():
            return list[MenuEntry]([
                MenuAction(
                    "Edit",
                    lambda s=subject: (self.showWindow(s), None)[1]
                ),
                MenuAction(
                    "New Window",
                    lambda s=subject: (self.newWindow(s), None)[1]
                ),
                MenuSeparator(),
                MenuAction(
                    "Duplicate",
                    lambda s=subject: self.duplicateSymbolHandler(s)
                ),
                MenuAction(
                    "Delete",
                    lambda s=subject: self.deleteSymbolHandler(s),
                    len(self._object.symbolDefinitionInstances(subject)) == 0
                ),
                MenuSeparator(),
                MenuAction(
                    "Refresh",
                    lambda s=subject: self.refreshSymbolHandler(s)
                ),
                MenuAction(
                    "Replace",
                    lambda s=subject: self.replaceSymbolHandler(s)
                ),
            ])
        return []

    # --- MDI (subwindows) -----------------------------------------------------

    @checked
    def showWindow(self : Self, subject : DocSubjectProtocol) -> bool:
        """
        Show existing primary editing subwindow for subject, or creates a new
        one if none exists. Ignores auxilliary editors (spreadsheets etc).
        """
        from ....widgets.graphics.views.diagram import DiagramSubWindow
        from ....widgets.graphics.views.symbol  import SymbolSubWindow
        subwindows = window().mdiArea().docSubjectSubWindows(self, subject)
        for subwindow in subwindows:
            if isinstance(subwindow, DiagramSubWindow | SymbolSubWindow):
                window().mdiArea().activateSubWindow(subwindow)
                return True
        return self.newWindow(subject)

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
            return self._object.name() + " - HDL Schematic Editor"
        if subject in self._object.getSymbols().values():
            return subject.name() + " - HDL Schematic Symbol Editor"
        return "Unknown Subject"

    @checked
    def mayCloseSubWindow(self : Self, subwindow : DocSubWindow) -> bool:
        """Prompt for commit/discard, and veto if necessary."""
        from ....widgets.graphics.items.symbol import SymbolDefinitionItem
        # get subject
        subject = self._subjectFromSubwindow(subwindow)
        if subject is self._object:
            return True
        elif isinstance(subject, SymbolDefinitionItem) \
        and subject in self._scenes:
            if self._isSymbolClean(subject):
                return True
            subwindows = window().mdiArea().docSubjectSubWindows(self, subject)
            if len(subwindows) == 1:
                defname = "Symbol" if isinstance(subject, SymbolDefinitionItem) \
                    else "Block"
                dialog = UnsavedChangesDialog(
                    f"{defname} '{subject.name()}' has been modified.",
                    window()
                )
                if dialog.exec() and dialog.commit():
                    self.commit(subwindow)
                    self._scenes[subject].undo_stack.setClean()
                    return True
                else:
                    return False
            return True
        else:
            raise RuntimeError("Bad subject")

    @checked
    def onSubWindowClosed(self : Self, subwindow : DocSubWindow) -> None:
        # get subject
        subject = self._subjectFromSubwindow(subwindow)
        if subject is None: return
        # clean up _symbol_scenes, update _dirty
        subwindows = window().mdiArea().docSubjectSubWindows(self, subject)
        if len(subwindows) == 1:
                if isinstance(subject, SymbolDefinitionItem) \
                and subject in self._scenes:
                    scene = self._scenes[subject]
                    if not scene.undo_stack.isClean():
                        self._modified.append(subject)
                    del self._scenes[subject]
        # clean up display labels
        window().mdiArea().onSubWindowsChanged()

    # --- editor lifecycle (close / save) --------------------------------------

    @checked
    def commit(self : Self, subwindow : DocSubWindow) -> None:
        subject = self._subjectFromSubwindow(subwindow)
        if subject is self._object:
            window().navigator().fileSave(subwindow)
        elif isinstance(subject, SymbolDefinitionItem):
            scene = self._scenes[subject]
            if isinstance(scene, SymbolScene):
                item = scene.symbol()
                if item is None:
                    raise RuntimeError("Scene has no item")
                subject.syncFromDefinition(item)
            else:
                raise RuntimeError("Bad scene")
            scene.undo_stack.setClean()
        else:
            raise RuntimeError("Bad subject")

    @checked
    def isPrimarySubject(self : Self, subject : DocSubjectProtocol) -> bool:
        return subject is self._object

    # --- menu action handlers -------------------------------------------------

    def newSymbolHandler(self : Self) -> None:
        # add new symbol definition to scene and navigator
        raise NotImplementedError("Not implemented")
        #self._scene.newSymbol()  # scene API (undoable)

        #self._scene.refreshSymbols()  # scene API (undoable)

        #self._scene.purgeSymbols()  # scene API (undoable)

    def duplicateSymbolHandler(
        self    : Self,
        subject : DocSubjectProtocol
    ) -> None:
        # duplicate symbol definition in scene and navigator
        raise NotImplementedError("Not implemented")
        #self._scene.duplicateSymbol(subject)  # scene API (undoable)

    def deleteSymbolHandler(
        self    : Self,
        subject : DocSubjectProtocol
    ) -> None:
        # delete symbol definition from scene and navigator
        raise NotImplementedError("Not implemented")
        #self._scene.deleteSymbol(subject)  # scene API (undoable)

    def refreshSymbolHandler(
        self    : Self,
        subject : DocSubjectProtocol
    ) -> None:
        # refresh symbol definition in scene and navigator
        raise NotImplementedError("Not implemented")
        #self._scene.refreshSymbol(subject)  # scene API (undoable)

    def replaceSymbolHandler(
        self    : Self,
        subject : DocSubjectProtocol
    ) -> None:
        # replace symbol definition in scene and navigator
        raise NotImplementedError("Not implemented")
        #self._scene.replaceSymbol(subject)  # scene API (undoable)

    # --- helpers --------------------------------------------------------------

    def _createSubWindow(
        self    : Self,
        subject : DocSubjectProtocol,
    ) -> DocSubWindow | None:
        if self._object is None:
            logger().error(f"{type(self).__name__} has no scene")
            return None
        from ....widgets.graphics.views.diagram import DiagramView, DiagramSubWindow
        from ....widgets.graphics.scenes.symbol import SymbolScene
        from ....widgets.graphics.views.symbol  import SymbolView, SymbolSubWindow
        from ....widgets.graphics.items.symbol  import SymbolDefinitionItem
        symbols = self._object.getSymbols().values()
        if subject is not self._object and subject not in symbols:
            logger().error(f"Document does not contain subject {subject}")
            return None
        binding = DocBinding(self, subject)
        mdi_area = window().mdiArea()
        if subject is self._object:
            scene = self._object
            view = DiagramView(scene)
            subwindow = DiagramSubWindow(mdi_area, binding)
        elif isinstance(subject, SymbolDefinitionItem):
            if subject not in self._scenes:
                scene = SymbolScene(subject.clone())
                scene.undo_stack.setClean()
                scene.undo_stack.cleanChanged.connect(
                    lambda clean, s=subject: self._onCleanChanged(s, clean)
                )
                self._scenes[subject] = scene
                if subject in self._modified:
                    self._modified.remove(subject)
            else:
                scene = self._scenes[subject]
            view = SymbolView(scene)
            subwindow = SymbolSubWindow(mdi_area, binding)
        else:
            raise RuntimeError("Bad subject")
        subwindow.setWidget(view)
        mdi_area.addSubWindow(subwindow)
        return subwindow

    def _isSymbolClean(self : Self, subject : DocSubjectProtocol) -> bool:
        from ....widgets.graphics.items.symbol import SymbolDefinitionItem
        if not isinstance(subject, SymbolDefinitionItem):
            raise TypeError("Bad subject")
        if subject in self._scenes:
            return self._scenes[subject].undo_stack.isClean()
        return subject not in self._modified

    def _modifiedSymbolsCount(self : Self) -> int:
        return sum(
            1 for symbol in self._object.getSymbols().values()
            if not self._isSymbolClean(symbol)
        )

    def _onCleanChanged(
        self    : Self,
        subject : DocSubjectProtocol,
        clean   : bool
    ) -> None:
        from ....widgets.graphics.items.symbol import SymbolDefinitionItem
        if isinstance(subject, SymbolDefinitionItem):
            if not clean:
                if subject not in self._modified:
                    self._modified.append(subject)
            else:
                if subject in self._modified:
                    self._modified.remove(subject)
        elif subject is not self._object:
            raise TypeError("Bad subject")
        self.onChanged()


# register document type with Session

Session.registerDocType(DocType(
    name  = "HDL Schematic Diagram",
    group = "HDL Schematic Diagrams",
    ext   = "sch.hdl",
    cls   = HdlSchematicDiagramDoc,
))
