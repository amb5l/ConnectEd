from typing import Self

from PyQt6.QtCore    import QSize, QXmlStreamWriter, QXmlStreamReader

from ..app       import logger, window
from ..resources import getIconPath

from ..core.check   import checked
from ..core.session import DocType, Session
from ..core.types   import MenuAction, MenuSeparator, MenuEntry
from ..core.doc     import NavItemSpec, DocSubjectProtocol, Doc, DocBinding
from ..core.icon    import SvgIconSingleton

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..widgets.window.sub_window import DocSubWindow
    from ..widgets.graphics.scenes.diagram import DiagramScene


class SchematicIcon(SvgIconSingleton):
    PATH = getIconPath("schematic.svg")
    SIZE = QSize(16, 16)


class SymbolIcon(SvgIconSingleton):
    PATH = getIconPath("symbol.svg")
    SIZE = QSize(16, 16)


class HdlSchematicDiagramDoc(Doc):
    _XML_TAG = "HdlSchematicDiagram"

    _scene : "DiagramScene | None"
    _path  : str

    def __init__(self : Self, name : str | None = None) -> None:
        from ..widgets.graphics.scenes.diagram import DiagramScene
        self._path = ""
        self._scene = DiagramScene(self)
        self.setName(name or "Untitled")

    def name(self : Self) -> str:
        return self._scene.name()

    def setName(self : Self, name : str) -> None:
        self._scene.setName(name)

    def path(self : Self) -> str:
        return self._path

    def setPath(self : Self, path : str) -> None:
        from ..core.utils import cleanPath
        path = cleanPath(path)
        if path == self._path:
            return
        self._path = path
        self.onChanged()

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self._scene.toXml(xw)

    @classmethod
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
        from ..core.utils import cleanPath
        from ..core.xml import loadXml
        return loadXml(cleanPath(path), {cls.tag(): cls})

    # --- Navigator (tree presentation) ----------------------------------------

    @checked
    def navItemSpec(self : Self) -> NavItemSpec:
        return NavItemSpec(
            subject  = self._scene,
            icon     = SchematicIcon(),  # TODO remove this, containers don't have icons
            tip      = self._path or "(not saved)",
            children = [
                NavItemSpec(
                    subject  = "Symbol Definitions",
                    children = [
                        NavItemSpec(subject = symbol_item, icon = SymbolIcon())
                        for symbol_item in self._scene.symbols()
                    ],
                ),
            ],
        )

    def navLabel(
        self    : Self,
        subject : DocSubjectProtocol | None = None,
    ) -> str:
        if subject is None:
            subject = self._scene
        return subject.name()

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

    def navToolTip(
        self    : Self,
        subject : DocSubjectProtocol
    ) -> str | None:
        return self._path or "(not saved)" if subject is self._scene else None

    def navContextMenu(
        self    : Self,
        subject : DocSubjectProtocol | None = None,
    ) -> list[MenuEntry]:
        if self._scene is None: return []
        if subject is None: subject = self._scene
        if subject is self._scene:
            nav = window().navigator()
            return [
                MenuAction("Save", lambda: nav.docSave(self)),
                MenuAction("Save As...", lambda: nav.docSaveAsPrompt(self)),
                MenuAction("Close", lambda: nav.docClose(self)),
                MenuSeparator(),
                MenuAction("Edit", lambda s=subject: self.showWindow(s)),
                MenuAction("New Window", lambda s=subject: self.newWindow(s)),
            ]
        elif subject == "Symbol Definitions":
            return [
                MenuAction("New Symbol", lambda: self.newSymbolHandler()),
                MenuSeparator(),
                MenuAction("Refresh All", lambda: self.refreshSymbolsHandler()),
                MenuAction("Purge All", lambda: self.purgeSymbolsHandler()),
            ]
        elif subject in self._scene.symbols():
            return [
                MenuAction("Edit", lambda s=subject: self.showWindow(s)),
                MenuAction("New Window", lambda s=subject: self.newWindow(s)),
                MenuSeparator(),
                MenuAction(
                    "Duplicate",
                    lambda s=subject: self.duplicateSymbolHandler(s)
                ),
                MenuAction(
                    "Delete",
                    lambda s=subject: self.deleteSymbolHandler(s),
                    self._scene.symbolInstances(subject) > 0
                ),
                MenuSeparator(),
                MenuAction(
                    "Refresh",
                    lambda s=subject: self.refreshSymbolHandler(s)
                ),
                MenuAction("Replace", lambda s=subject: self.replaceSymbolHandler(s)),
            ]
        return []

    # --- MDI (subwindows) -----------------------------------------------------

    def _findSubWindow(
        self    : Self,
        subject : DocSubjectProtocol,
    ) -> "DocSubWindow | None":
        from ..widgets.window.sub_window import DocSubWindow
        mdi_area = window().mdiArea()
        for existing in mdi_area.subWindowList():
            if not isinstance(existing, DocSubWindow):
                continue
            binding = existing.docBinding()
            if binding is None:
                continue
            if binding.doc != self:
                continue
            if binding.subject is subject:
                return existing
        return None

    def _createSubWindow(
        self    : Self,
        subject : DocSubjectProtocol,
    ) -> "DocSubWindow | None":
        if self._scene is None:
            logger().error(f"{type(self).__name__} has no scene")
            return None
        from ..widgets.graphics.views.diagram  import DiagramView, DiagramSubWindow
        from ..widgets.graphics.views.symbol   import SymbolView, SymbolSubWindow
        from ..widgets.graphics.scenes.diagram import DiagramScene
        from ..widgets.graphics.scenes.symbol  import SymbolScene
        from ..widgets.graphics.items.symbol   import SymbolItem
        symbols = self._scene.symbols()
        if subject is not self._scene and subject not in symbols:
            logger().error(f"Document does not contain subject {subject}")
            return None
        if isinstance(subject, DiagramScene):
            scene = subject
            view_cls = DiagramView
            subwindow_cls = DiagramSubWindow
        elif isinstance(subject, SymbolItem):
            scene = SymbolScene()
            scene.addItem(subject.clone())
            view_cls = SymbolView
            subwindow_cls = SymbolSubWindow
        else:
            logger().error(f"Unsupported subject type: {type(subject)}")
            return None
        view = view_cls(scene)
        binding = DocBinding(self, subject)
        mdi_area = window().mdiArea()
        subwindow = subwindow_cls(mdi_area, binding)
        subwindow.setWidget(view)
        mdi_area.addSubWindow(subwindow)
        return subwindow

    def showWindow(self : Self, subject : DocSubjectProtocol) -> bool:
        subwindow = self._findSubWindow(subject)
        if subwindow is not None:
            window().mdiArea().activateSubWindow(subwindow)
            return True
        return self.newWindow(subject)

    def newWindow(self : Self, subject : DocSubjectProtocol) -> bool:
        subwindow = self._createSubWindow(subject)
        if subwindow is None:
            return False
        subwindow.showMaximized()
        window().mdiArea().activateSubWindow(subwindow)
        return True

    def windowTitle(self : Self, subject : DocSubjectProtocol) -> str:
        if subject is self._scene:
            return self._scene.name() + " - HDL Schematic Editor"
        if subject in self._scene.symbols():
            return subject.name() + " - HDL Schematic Symbol Editor"
        return "Unknown Subject"

    # --- editor lifecycle (close / save) --------------------------------------

    def isPrimarySubject(self : Self, subject : DocSubjectProtocol) -> bool:
        return subject is self._scene

    # --- menu action handlers -------------------------------------------------

    def newSymbolHandler(self : Self) -> None:
        # add new symbol definition to scene and navigator
        self._scene.newSymbol()  # scene API (undoable)

    def refreshSymbolsHandler(self : Self) -> None:
        # refresh all symbol definitions in scene and navigator
        self._scene.refreshSymbols()  # scene API (undoable)

    def purgeSymbolsHandler(self : Self) -> None:
        # purge all symbol definitions from scene and navigator
        self._scene.purgeSymbols()  # scene API (undoable)

    def duplicateSymbolHandler(
        self : Self,
        subject : DocSubjectProtocol
    ) -> None:
        # duplicate symbol definition in scene and navigator
        self._scene.duplicateSymbol(subject)  # scene API (undoable)

    def deleteSymbolHandler(
        self : Self,
        subject : DocSubjectProtocol
    ) -> None:
        # delete symbol definition from scene and navigator
        self._scene.deleteSymbol(subject)  # scene API (undoable)

    def refreshSymbolHandler(
        self : Self,
        subject : DocSubjectProtocol
    ) -> None:
        # refresh symbol definition in scene and navigator
        self._scene.refreshSymbol(subject)  # scene API (undoable)

    def replaceSymbolHandler(
        self : Self,
        subject : DocSubjectProtocol
    ) -> None:
        # replace symbol definition in scene and navigator
        self._scene.replaceSymbol(subject)  # scene API (undoable)



# register document type with Session

DOC_TYPE = DocType(
    name  = "HDL Schematic Diagram",
    group = "HDL Schematic Diagrams",
    ext   = "hdl_sch",
    cls   = HdlSchematicDiagramDoc,
)

Session.registerDocType(DOC_TYPE)
