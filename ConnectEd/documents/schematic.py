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

from ..app       import logger, window
from ..resources import getIconPath

from ..core.check   import checked
from ..core.session import DocType, Session
from ..core.types   import MenuAction, MenuSeparator, MenuEntry
from ..core.doc     import NavItemSpec, DocSubjectProtocol, Doc, DocBinding
from ..core.icon    import SvgIconSingleton
from ..core.xml     import loadXml
from ..core.utils   import cleanPath

from ..widgets.dialogs.unsaved_changes import UnsavedChangesDialog

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..widgets.window.sub_window       import DocSubWindow
    from ..widgets.graphics.scenes.diagram import DiagramScene
    from ..widgets.graphics.scenes.symbol  import SymbolScene

from ..widgets.graphics.items.symbol   import SymbolDefinitionItem


_SYMBOL_CONTAINER = "Symbols"


class SchematicIcon(SvgIconSingleton):
    PATH = getIconPath("schematic.svg")
    SIZE = QSize(16, 16)


class SymbolIcon(SvgIconSingleton):
    PATH = getIconPath("symbol.svg")
    SIZE = QSize(16, 16)


class HdlSchematicDiagramDoc(Doc):
    _XML_TAG = "HdlSchematicDiagram"

    _path             : str
    _scene            : DiagramScene
    _symbol_container : str
    _symbol_scenes    : dict[SymbolDefinitionItem, SymbolScene]
    _dirty            : list[SymbolDefinitionItem | str]

    @checked
    def __init__(self : Self, name : str | None = None) -> None:
        from ..widgets.graphics.scenes.diagram import DiagramScene
        self._path = ""
        self._scene = DiagramScene(self)
        self._symbol_container = _SYMBOL_CONTAINER
        self._symbol_scenes = {}
        self._dirty = []
        self.setName(name or "Untitled")
        undo_stack = self._scene.undo_stack
        undo_stack.setClean()
        undo_stack.cleanChanged.connect(
            lambda clean: self._onCleanChanged(self._scene, clean)
        )

    # --- clean state tracking -------------------------------------------------

    @checked
    def isClean(
        self    : Self,
        subject : DocSubjectProtocol | None = None
    ) -> bool:
        from ..widgets.graphics.scenes.diagram import DiagramScene
        if subject is None:
            subject = self._scene
        if isinstance(subject, DiagramScene):
            return subject.undo_stack.isClean() and self._dirtySymbolCount() == 0
        elif isinstance(subject, SymbolDefinitionItem):
            if subject in self._symbol_scenes:
                return self._symbol_scenes[subject].undo_stack.isClean()
            else:
                return subject in self._dirty
        else:
            logger().error(f"Unsupported subject type: {type(subject)}")
            return False

    @checked
    def name(self : Self) -> str:
        return self._scene.name()

    @checked
    def setName(self : Self, name : str) -> None:
        self._scene.setName(name)

    @checked
    def path(self : Self) -> str:
        return self._path

    @checked
    def setPath(self : Self, path : str) -> None:
        path = cleanPath(path)
        if path == self._path:
            return
        self._path = path
        self.onChanged()

    @checked
    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self._scene.toXml(xw)

    @classmethod
    @checked
    def fromXml(
        cls : type[Self],
        xr  : QXmlStreamReader,
    ) -> Self:
        from ..widgets.graphics.scenes.diagram import DiagramScene
        doc = cls()
        scene = DiagramScene.fromXml(xr)
        scene._doc = doc
        doc._scene = scene
        return doc

    @classmethod
    @checked
    def load(cls : type[Self], path : str) -> Self | None:
        return cast(Self, loadXml(cleanPath(path), {cls.tag(): cls}))

    @checked
    def save(self : Self, path : str | None = None) -> bool:
        self._scene.undo_stack.setClean()
        self._dirty = []
        return super().save(path)

    # --- Navigator (tree presentation) ----------------------------------------

    @checked
    def navItemSpec(self : Self) -> NavItemSpec:
        return NavItemSpec(
            subject  = self._scene,
            icon     = SchematicIcon().get(),  # TODO remove this, containers don't have icons
            tip      = self._path or "(not saved)",
            children = [
                NavItemSpec(
                    subject  = self._symbol_container,
                    children = [
                        NavItemSpec(subject = s, icon = SymbolIcon().get())
                        for s in self._scene.symbolDefinitions().values()
                    ],
                ),
            ],
        )

    @checked
    def navLabel(
        self    : Self,
        subject : DocSubjectProtocol | None = None,
    ) -> str:
        if subject is None:
            subject = self._scene
        return subject.name()

    @checked
    def navSetLabel(
        self    : Self,
        subject : DocSubjectProtocol | None,
        label   : str,
    ) -> bool:
        if subject is None:
            subject = self._scene
        if subject is self._scene:
            if label == subject.name():
                return False
            self._scene.setName(label, notify=False)
            window().mdiArea().onSubWindowsChanged()
            return True
        return False

    @checked
    def navDisplayLabel(
        self    : Self,
        subject : DocSubjectProtocol | None = None,
    ) -> str:
        if subject is None:
            subject = self._scene
        return subject.name() + ("" if self.isClean(subject) else "*")

    @checked
    def navToolTip(
        self    : Self,
        subject : DocSubjectProtocol | None = None
    ) -> str | None:
        return self._path or "(not saved)" if subject is self._scene else None

    @checked
    def navContextMenu(
        self    : Self,
        subject : DocSubjectProtocol | None = None,
    ) -> list[MenuEntry]:
        if self._scene is None: return []
        if subject is None: subject = self._scene
        if subject is self._scene:
            nav = window().navigator()
            return list[MenuEntry]([
                MenuAction("Save", lambda: nav.docSave(self)),
                MenuAction("Save As...", lambda: nav.docSaveAsPrompt(self)),
                MenuAction("Close", lambda: nav.docClose(self)),
                MenuSeparator(),
                MenuAction(
                    "Edit",
                    lambda s=subject: (self.showWindow(s), None)[1]
                ),
                MenuAction(
                    "New Window",
                    lambda s=subject: (self.newWindow(s), None)[1]
                ),
            ])
        elif subject == self._symbol_container:
            return list[MenuEntry]([
                MenuAction("New Symbol", lambda: self.newSymbolHandler()),
                MenuSeparator(),
                MenuAction(
                    "Refresh All",
                    lambda: self.refreshSymbolsHandler()
                ),
                MenuAction(
                    "Purge All",
                    lambda: self.purgeSymbolsHandler()
                ),
            ])
        elif isinstance(subject, SymbolDefinitionItem) \
        and subject in self._scene.symbolDefinitions().values():
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
                    len(self._scene.symbolInstances(subject)) == 0
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
        from ..widgets.graphics.views.diagram import DiagramSubWindow
        from ..widgets.graphics.views.symbol  import SymbolSubWindow
        subwindows = window().mdiArea().docSubjectSubWindows(self, subject)
        subwindow = None
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
        if subject is self._scene:
            return self._scene.name() + " - HDL Schematic Editor"
        if subject in self._scene.symbolDefinitions().values():
            return subject.name() + " - HDL Schematic Symbol Editor"
        return "Unknown Subject"

    @checked
    def closeSubWindow(self : Self, subwindow : DocSubWindow) -> bool:
        """Prompt for commit/discard, and veto if necessary."""
        from ..widgets.graphics.scenes.diagram import DiagramScene
        from ..widgets.graphics.items.symbol   import SymbolDefinitionItem
        # get subject
        subject = self._subjectFromSubwindow(subwindow)
        if subject is None: return False
        # prompt to save/commit when last window is closed
        if isinstance(subject, DiagramScene):
            # whole document
            subwindows = window().mdiArea().docSubWindows(self)
            if len(subwindows) == 1:
                window().navigator().fileSaveAs(subwindow)
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
                    scene = self._symbol_scenes[subject]
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
        # clean up _symbol_scenes, update _dirty
        subwindows = window().mdiArea().docSubjectSubWindows(self, subject)
        if len(subwindows) == 1:
                if isinstance(subject, SymbolDefinitionItem) \
                and subject in self._symbol_scenes:
                    scene = self._symbol_scenes[subject]
                    if not scene.undo_stack.isClean():
                        self._dirty.append(subject)
                    del self._symbol_scenes[subject]
        # clean up display labels
        window().mdiArea().onSubWindowsChanged()

    # --- editor lifecycle (close / save) --------------------------------------

    @checked
    def commit(self : Self, subwindow : DocSubWindow) -> bool:
        from ..widgets.graphics.scenes.diagram import DiagramScene
        from ..widgets.graphics.items.symbol   import SymbolDefinitionItem
        subject = self._subjectFromSubwindow(subwindow)
        if subject is None: return False
        if isinstance(subject, DiagramScene):
            window().navigator().fileSave(subwindow)
            return True
        elif isinstance(subject, SymbolDefinitionItem):
            scene = self._symbol_scenes[subject]
            subject.syncFromScene(scene)
            scene.undo_stack.setClean()
            return True
        logger().error(f"Unsupported subject type: {type(subject)}")
        return False

    @checked
    def isPrimarySubject(self : Self, subject : DocSubjectProtocol) -> bool:
        return subject is self._scene

    # --- menu action handlers -------------------------------------------------

    def newSymbolHandler(self : Self) -> None:
        # add new symbol definition to scene and navigator
        raise NotImplementedError("Not implemented")
        #self._scene.newSymbol()  # scene API (undoable)

    def refreshSymbolsHandler(self : Self) -> None:
        # refresh all symbol definitions in scene and navigator
        raise NotImplementedError("Not implemented")
        #self._scene.refreshSymbols()  # scene API (undoable)

    def purgeSymbolsHandler(self : Self) -> None:
        # purge all symbol definitions from scene and navigator
        raise NotImplementedError("Not implemented")
        #self._scene.purgeSymbols()  # scene API (undoable)

    def duplicateSymbolHandler(
        self : Self,
        subject : DocSubjectProtocol
    ) -> None:
        # duplicate symbol definition in scene and navigator
        raise NotImplementedError("Not implemented")
        #self._scene.duplicateSymbol(subject)  # scene API (undoable)

    def deleteSymbolHandler(
        self : Self,
        subject : DocSubjectProtocol
    ) -> None:
        # delete symbol definition from scene and navigator
        raise NotImplementedError("Not implemented")
        #self._scene.deleteSymbol(subject)  # scene API (undoable)

    def refreshSymbolHandler(
        self : Self,
        subject : DocSubjectProtocol
    ) -> None:
        # refresh symbol definition in scene and navigator
        raise NotImplementedError("Not implemented")
        #self._scene.refreshSymbol(subject)  # scene API (undoable)

    def replaceSymbolHandler(
        self : Self,
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
        if self._scene is None:
            logger().error(f"{type(self).__name__} has no scene")
            return None
        from ..widgets.graphics.views.diagram  import DiagramView, DiagramSubWindow
        from ..widgets.graphics.views.symbol   import SymbolView, SymbolSubWindow
        from ..widgets.graphics.scenes.diagram import DiagramScene
        from ..widgets.graphics.scenes.symbol  import SymbolScene
        from ..widgets.graphics.items.symbol   import SymbolDefinitionItem
        symbols = self._scene.symbolDefinitions().values()
        if subject is not self._scene and subject not in symbols:
            logger().error(f"Document does not contain subject {subject}")
            return None
        binding = DocBinding(self, subject)
        mdi_area = window().mdiArea()
        if isinstance(subject, DiagramScene):
            scene = subject
            view = DiagramView(scene)
            subwindow = DiagramSubWindow(mdi_area, binding)
        elif isinstance(subject, SymbolDefinitionItem):
            if subject not in self._symbol_scenes:
                scene = SymbolScene()
                scene.addItem(subject.clone())
                scene.undo_stack.setClean()
                scene.undo_stack.cleanChanged.connect(
                    lambda clean, s=subject: self._onCleanChanged(s, clean)
                )
                self._symbol_scenes[subject] = scene
                if subject in self._dirty:
                    self._dirty.remove(subject)
            else:
                scene = self._symbol_scenes[subject]
            view = SymbolView(scene)
            subwindow = SymbolSubWindow(mdi_area, binding)
        else:
            logger().error(f"Unsupported subject type: {type(subject)}")
            return None
        subwindow.setWidget(view)
        mdi_area.addSubWindow(subwindow)
        return subwindow

    def _isSymbolClean(self : Self, subject : DocSubjectProtocol) -> bool:
        from ..widgets.graphics.items.symbol import SymbolDefinitionItem
        if not isinstance(subject, SymbolDefinitionItem):
            raise TypeError("Bad subject")
        if subject in self._symbol_scenes:
            return self._symbol_scenes[subject].undo_stack.isClean()
        return subject not in self._dirty

    def _dirtySymbolCount(self : Self) -> int:
        return sum(
            1 for symbol in self._scene.symbolDefinitions().values()
            if not self._isSymbolClean(symbol)
        )

    def _onCleanChanged(
        self    : Self,
        subject : DocSubjectProtocol,
        clean   : bool
    ) -> None:
        from ..widgets.graphics.items.symbol import SymbolDefinitionItem
        if not isinstance(subject, SymbolDefinitionItem):
            raise TypeError("Bad subject")
        if not clean:
            if subject not in self._dirty:
                self._dirty.append(subject)
            if isinstance(subject, SymbolDefinitionItem):
                if self._symbol_container not in self._dirty:
                    self._dirty.append(self._symbol_container)
        else:
            if subject in self._dirty:
                self._dirty.remove(subject)
            if self._symbol_container in self._dirty:
                if self._dirtySymbolCount() == 0:
                    self._dirty.remove(self._symbol_container)
        self.onChanged()

    def _subjectFromSubwindow(
        self      : Self,
        subwindow : DocSubWindow
    ) -> DocSubjectProtocol | None:
        if (binding := subwindow.docBinding()) is None:
            logger().error("Subwindow has no binding")
            return None
        if binding.doc is not self:
            logger().error(f"Subwindow has wrong document: {binding.doc} != {self}")
            return None
        return binding.subject


# register document type with Session

DOC_TYPE = DocType(
    name  = "HDL Schematic Diagram",
    group = "HDL Schematic Diagrams",
    ext   = "hdl_sch",
    cls   = HdlSchematicDiagramDoc,
)

Session.registerDocType(DOC_TYPE)
