from typing import Self

from PyQt6.QtCore    import QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QWidget

from ..app import logger, window

from ..core.check   import checked
from ..core.doc     import NavItemSpec, Doc, DocBinding
from ..core.session import Session

from ..widgets.window.sub_window import DocSubWindow

from ..widgets.graphics.views.diagram  import DiagramView, DiagramSubWindow
from ..widgets.graphics.views.symbol   import SymbolView, SymbolSubWindow
from ..widgets.graphics.scenes.diagram import DiagramScene
from ..widgets.graphics.scenes.symbol  import SymbolScene
from ..widgets.graphics.items.symbol   import SymbolItem


class SchematicDoc(Doc):
    # class attributes
    _display_name = "Schematic Diagram"

    # instance attributes
    _scene : "DiagramScene | None"
    _path  : str

    def __init__(self : Self) -> None:
        self._path = ""

    def path(self : Self) -> str:
        return self._path

    def setPath(self : Self, path : str) -> None:
        self._path = path

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self._scene.toXml(xw)

    @classmethod
    def fromXml(cls : type[Self], xr : QXmlStreamReader) -> Self:
        doc = cls()
        doc._scene = DiagramScene.fromXml(xr)
        return doc

    # --- Navigator tree -------------------------------------------------------

    @checked
    def navigatorChildren(self : Self) -> list[NavItemSpec]:
        return [
            NavItemSpec(
                id       = "symbol_cache",
                label    = "Symbols",       # static label
                subject  = None,
                open     = None,            # not openable => container
                children = [
                    NavItemSpec(sym.id(), sym.name(), DocNavKind.SYMBOL)
                    for sym in self._scene.symbolDefinitions()
                ],
            )
        ]

    @checked
    def navigatorItem(self : Self, child_id : str) -> NavItemSpec | None:
        """Look up one child row by id."""
        for item in self.navigatorChildren():
            if item.id == child_id:
                return item
        return None

    @checked
    def renameNavigatorChild(self : Self, child_id : str, label : str) -> None:
        """Rename a child row (e.g. symbol name). Override when ``editable``."""
        raise NotImplementedError(
            f"{type(self).__name__} does not support renaming child {child_id!r}"
        )

    # --- open / edit (Navigator, MDI) -----------------------------------------

    @abstractmethod
    def openDefault(self : Self) -> None:
        """
        Open or focus the primary editor for this document
        (e.g. schematic diagram, library container).
        """

    @checked
    def openChild(self : Self, child_id : str) -> None:
        """
        Open or focus an editor for one Navigator child row
        (e.g. symbol definition in a library).
        """
        raise NotImplementedError(
            f"{type(self).__name__} does not support openChild({child_id!r})"
        )

    # --- window management ----------------------------------------------------

    def openWindow(self : Self, widget : QWidget) -> DocSubWindow | None:
        symbols = self._scene.symbols()
        if widget is not self._scene and widget not in symbols:
            logger().error(f"Document does not contain widget {widget}")
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
            if doc_binding.widget is widget:
                break  # subwindow is already open
        else:
            if isinstance(widget, DiagramScene):
                scene = widget
                view_cls = DiagramView
                subwindow_cls = DiagramSubWindow
            elif isinstance(widget, SymbolItem):
                scene = SymbolScene()
                scene.addItem(widget.clone())
                view_cls = SymbolView
                subwindow_cls = SymbolSubWindow
            else:
                logger().error(f"Unsupported widget type: {type(widget)}")
                return None
            view = view_cls(scene)
            doc_binding = DocBinding(self, widget)
            subwindow = subwindow_cls(mdi_area, doc_binding)
            subwindow.setWidget(view)
            mdi_area.addSubWindow(subwindow)
        mdi_area.activateSubWindow(subwindow)
        mdi_area.update()
        return subwindow


Session.registerDocType(
    "Schematic Diagram",   # friendly document type name
    "Schematic Diagrams",  # friendly document group name
    ".sch",                # file extension
    "Schematic",           # XML tag
    SchematicDoc           # class
)
