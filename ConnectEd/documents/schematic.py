from typing import Self

from PyQt6.QtCore    import QSize, QXmlStreamWriter, QXmlStreamReader

from ..app       import logger, window
from ..resources import getIconPath

from ..core.check   import checked
from ..core.session import Session
from ..core.doc     import (
    Doc,
    DocBinding,
    DocSubjectProtocol,
    NavItemSpec,
    NavMenuAction,
    NavMenuItem
)
from ..core.icon import SvgIconSingleton

from ..widgets.window.sub_window import DocSubWindow

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..widgets.graphics.scenes.diagram import DiagramScene


class SchematicIcon(SvgIconSingleton):
    PATH = getIconPath("schematic.svg")
    SIZE = QSize(16, 16)


class SymbolIcon(SvgIconSingleton):
    PATH = getIconPath("symbol.svg")
    SIZE = QSize(16, 16)


class HdlSchematicDiagramDoc(Doc):
    _scene : "DiagramScene | None"
    _path  : str

    def __init__(self : Self) -> None:
        self._path = ""

    def path(self : Self) -> str:
        return self._path

    def setPath(self : Self, path : str) -> None:
        self._path = path

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self._scene.toXml(xw, self.__class__.__name__)

    @classmethod
    def fromXml(
        cls  : type[Self],
        xr   : QXmlStreamReader,
        path : str | None = None,
    ) -> Self:
        from ..widgets.graphics.scenes.diagram import DiagramScene
        doc = cls()
        doc._scene = DiagramScene.fromXml(xr)
        doc._path = path or ""
        return doc

    @classmethod
    def load(cls : type[Self], path : str) -> bool:
        raise NotImplementedError(
            f"{cls.__name__}.load({path!r}) is not implemented"
        )

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
        logger().warning(
            f"{type(self).__name__}.navSetLabel({subject!r}, {label!r}) "
            f"is not implemented"
        )
        return False

    def navToolTip(
        self    : Self,
        subject : DocSubjectProtocol
    ) -> str | None:
        return self._path or "(not saved)" if subject is self._scene else None

    def navContextMenu(
        self    : Self,
        subject : DocSubjectProtocol | None = None,
    ) -> list[NavMenuAction | NavMenuItem]:
        if self._scene is None:
            return []
        if subject is None or subject is self._scene:
            return [
                NavMenuAction.SAVE,
                NavMenuAction.SAVE_AS,
                NavMenuAction.CLOSE,
                NavMenuAction.SEPARATOR,
                NavMenuAction.EDIT,
                NavMenuAction.NEW_WINDOW,
            ]
        elif subject == "Symbol Definitions":
            return [
                NavMenuAction.NEW,
                NavMenuAction.SEPARATOR,
                NavMenuAction.EDIT,
                NavMenuAction.NEW_WINDOW,
                NavMenuAction.SEPARATOR,
                NavMenuItem(label = "Purge", handler = self.purgeSymbols)
            ]
        elif subject in self._scene.symbols():
            return [
                NavMenuAction.EDIT,
                NavMenuAction.NEW_WINDOW,
                NavMenuAction.SEPARATOR,
                NavMenuItem(label = "Refresh", handler = self.refreshSymbol),
                NavMenuItem(label = "Replace", handler = self.replaceSymbol)
            ]
        return []

    # --- MDI (subwindows) -------------------------------------------------------

    def _findSubWindow(
        self    : Self,
        subject : DocSubjectProtocol,
    ) -> DocSubWindow | None:
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
    ) -> DocSubWindow | None:
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
        created = False
        if subwindow is None:
            subwindow = self._createSubWindow(subject)
            if subwindow is None:
                return False
            created = True
        if created:
            subwindow.showMaximized()
        window().mdiArea().activateSubWindow(subwindow)
        return True

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

    # --- editor lifecycle (close / save) ----------------------------------------

    def isPrimarySubject(self : Self, subject : DocSubjectProtocol) -> bool:
        return subject is self._scene


Session.registerDocType(
    "HDL Schematic Diagram",   # friendly document type name
    "HDL Schematic Diagrams",  # friendly document group name
    ".hdl_sch",                # file extension
    "HdlSchematicDiagram",     # XML tag
    HdlSchematicDiagramDoc,    # class
)
