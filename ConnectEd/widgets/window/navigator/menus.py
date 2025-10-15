from PyQt6.QtGui import QAction

from ....app import logger

from ...menu import Menu

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Navigator


_MENU_SPECS = (
    ("DesignsDbContainer", (
        ( "New Design"  , "NewDesign"  ),
        ( "Open Design" , "OpenDesign" )
    )),
    ("LibrariesDbContainer", (
        ( "New Library"  , "NewLibrary"  ),
        ( "Open Library" , "OpenLibrary" )
    )),
    ("DesignDbNode", (
        ("New", (
            ( "Diagram" , "NewDiagram" ),
            ( "Symbol"  , "NewSymbol"  )
        )),
        ( "Save"    , "SaveDesign"   ),
        ( "Save As" , "SaveDesignAs" ),
        ( "Close"   , "CloseDesign"  ),
        "--",
        ( "Rename"  , "Rename"       )
    )),
    ("LibraryDbNode", (
        ( "New Symbol" , "NewSymbol"  ),
        "--",
        ( "Save"    , "SaveLibrary"   ),
        ( "Save As" , "SaveLibraryAs" ),
        ( "Close"   , "CloseLibrary"  ),
        "--",
        ( "Rename"  , "Rename"        )
    )),
    ("DiagramsContainer", (
        ( "New Diagram" , "NewDiagram" ),
    )),
    ("SymbolCacheContainer", (
        ( "New Symbol" , "NewSymbol" ),
    )),
    ("DiagramNode", (
        ( "Edit"       , "EditDrawing"      ),
        ( "Rename"     , "Rename"           ),
        "--",
        ( "Set Root"   , "SetRoot"          ),
        "--",
        ( "Properties" , "EditProperties"   )
    )),
    ("SymbolNode", (
        ( "Edit"       , "EditDrawing"      ),
        ( "Rename"     , "Rename"           ),
        ( "New Window" , "NewDrawingWindow" )
    )),
    ("DrawingWindowNode", (
        ( "Activate"  , "ActivateDrawingWindow"  ),
        ( "Duplicate" , "DuplicateDrawingWindow" ),
        ( "Close"     , "CloseDrawingWindow"     )
    )),
    ("SymbolWindowNode", (
        ( "Activate"  , "ActivateDrawingWindow"  ),
        ( "Duplicate" , "DuplicateDrawingWindow" ),
        ( "Close"     , "CloseDrawingWindow"     )
    ))
)

class NavigatorMenusMixin:

    # instance attributes
    menus : dict[str, Menu]

    def _initMenus(self : "Navigator") -> None:
        self.menus = {}
        for name, spec in _MENU_SPECS:
            self.menus[name] = self._buildMenu(spec)

    def _buildMenu(
        self : "Navigator",
        spec : tuple[str, str | tuple]
    ) -> Menu:
        # create empty menu
        menu = Menu(self)
        # add actions/submenus to menu
        for name, slot_or_spec in spec:
            if isinstance(slot_or_spec, str):
                if slot_or_spec.startswith("-"):  # it's a separator
                    action = QAction()
                    action.setSeparator(True)
                    menu.addSeparator()
                else:  # it's a slot name
                    action = QAction(name, self)
                    slot = getattr(self, "_slot" + slot_or_spec)
                    action.triggered.connect(slot)
                menu.addAction(action)
            elif isinstance(slot_or_spec, tuple):  # it's a submenu spec
                # this entry is a submenu
                submenu = self._buildMenu(slot_or_spec)
                menu.addMenu(submenu)
            else:
                logger().error(f"Unknown entry type: {slot_or_spec}")
                continue
        return menu

    def _slotNewDesign(self : "Navigator") -> None:
        self.newDesign()

    def _slotOpenDesign(self : "Navigator") -> None:
        self.openDesign()

    def _slotSaveDesign(self : "Navigator") -> None:
        self.save(self.node)

    def _slotSaveDesignAs(self : "Navigator") -> None:
        self.saveAs(self.node)

    def _slotCloseDesign(self : "Navigator") -> None:
        self.close(self.node)

    def _slotNewLibrary(self : "Navigator") -> None:
        self.newLibrary()

    def _slotOpenLibrary(self : "Navigator") -> None:
        self.openLibrary()

    def _slotSaveLibrary(self : "Navigator") -> None:
        self.saveLibrary(self.node)

    def _slotSaveLibraryAs(self : "Navigator") -> None:
        self.saveLibraryAs(self.node)

    def _slotCloseLibrary(self : "Navigator") -> None:
        self.closeLibrary(self.node)

    def _slotNewDiagram(self : "Navigator") -> None:
        self.newDiagram(self.node)

    def _slotNewSymbol(self : "Navigator") -> None:
        self.newSymbol(self.node)

    def _slotEditDrawing(self : "Navigator") -> None:
        self.editDrawing(self.node)

    def _slotNewDrawingWindow(self : "Navigator") -> None:
        self.newDrawingWindow(self.node)

    def _slotEditProperties(self : "Navigator") -> None:
        self.editProperties(self.node)

    def _slotSetRoot(self : "Navigator") -> None:
        self.setRoot(self.node)

    def _slotActivateDrawingWindow(self : "Navigator") -> None:
        self.activateDrawingWindow(self.node)

    def _slotDuplicateDrawingWindow(self : "Navigator") -> None:
        self.duplicateDrawingWindow(self.node)

    def _slotCloseDrawingWindow(self : "Navigator") -> None:
        self.closeDrawingWindow(self.node)

    def _slotRename(self : "Navigator") -> None:
        self.rename(self.node)

    def _slotCopy(self : "Navigator") -> None:
        self.copy(self.node)

    def _slotPaste(self : "Navigator") -> None:
        self.paste(self.node)
