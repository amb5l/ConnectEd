from typing import Self

from PyQt6.QtCore    import QSize, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QWidget

from ..app       import logger, window
from ..resources import getIconPath

from ..core.check   import checked
from ..core.session import Session
from ..core.doc     import DocSubjectProtocol, NavItemSpec, Doc, DocBinding
from ..core.icon    import SvgIconSingleton

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


class SchematicDoc(Doc):
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
        path : str | None = None
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

    # --- Navigator tree -------------------------------------------------------

    @checked
    def navItemSpec(self : Self) -> NavItemSpec:
        return NavItemSpec(
            subject  = self._scene,
            icon     = SchematicIcon(),
            tip      = self._path or "(not saved)",
            children = [
                NavItemSpec(
                    subject  = "Symbols",
                    children = [
                        NavItemSpec(subject = symbol_item, icon = SymbolIcon())
                        for symbol_item in self._scene.symbols()
                    ]
                )
            ]
        )

    def navOpen(self : Self, widget : DocSubjectProtocol) -> None:
        raise NotImplementedError(
            f"{type(self).__name__}.navOpen({widget!r}) is not implemented"
        )

    def navRename(
        self   : Self,
        widget : DocSubjectProtocol,
        name   : str,
    ) -> None:
        raise NotImplementedError(
            f"{type(self).__name__}.navRename({widget!r}, {name!r}) "
            f"is not implemented"
        )

    # --- open / edit (Navigator, MDI) -----------------------------------------

    def open(self : Self, widget : QWidget) -> None:
        raise NotImplementedError(
            f"{type(self).__name__}.open({widget!r}) is not implemented"
        )

    def openDefault(self : Self) -> None:
        raise NotImplementedError(
            f"{type(self).__name__}.openDefault() is not implemented"
        )

    # --- window management ----------------------------------------------------

    def newWindow(self : Self, widget : QWidget) -> None:
        raise NotImplementedError(
            f"{type(self).__name__}.newWindow({widget!r}) is not implemented"
        )

    def openWindow(self : Self, subject : QWidget) -> DocSubWindow | None:
        from ..widgets.graphics.views.diagram  import DiagramView, DiagramSubWindow
        from ..widgets.graphics.views.symbol   import SymbolView, SymbolSubWindow
        from ..widgets.graphics.scenes.diagram import DiagramScene
        from ..widgets.graphics.scenes.symbol  import SymbolScene
        from ..widgets.graphics.items.symbol   import SymbolItem
        symbols = self._scene.symbols()
        if subject is not self._scene and subject not in symbols:
            logger().error(f"Document does not contain widget {subject}")
            return None
        mdi_area = window().mdiArea()
        subwindows = mdi_area.subWindowList()
        for subwindow in subwindows:
            if not isinstance(subwindow, DocSubWindow):
                continue
            doc_binding = subwindow.docBinding()
            if doc_binding is None:
                continue
            if doc_binding.doc != self:
                continue
            if doc_binding.widget is subject:
                break  # subwindow is already open
        else:
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
                logger().error(f"Unsupported widget type: {type(subject)}")
                return None
            view = view_cls(scene)
            doc_binding = DocBinding(self, subject)
            subwindow = subwindow_cls(mdi_area, doc_binding)
            subwindow.setWidget(view)
            mdi_area.addSubWindow(subwindow)
        mdi_area.activateSubWindow(subwindow)
        mdi_area.update()
        return subwindow

    def windowTitle(self : Self, subject : DocSubjectProtocol) -> str:
        if subject is self._scene:
            return self._scene.name() + " - Schematic Editor"
        elif subject in self._scene.symbols():
            return subject.name() + " - Symbol Editor"
        return "Unknown Subject"


Session.registerDocType(
    "Schematic Diagram",    # friendly document type name
    "Schematic Diagrams",   # friendly document group name
    ".sch",                 # file extension
    "HdlSchematicDiagram",  # XML tag
    SchematicDoc            # class
)
