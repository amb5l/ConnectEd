from PyQt6.QtGui import QAction

from ....app import logger

from ...menu import Menu

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Navigator


_MENU_SPECS = (
    (None, (
        ( "New Design"  , "NewDesign"  ),
        ( "Open Design" , "OpenDesign" ),
        "--",
        ( "New Library"  , "NewLibrary"  ),
        ( "Open Library" , "OpenLibrary" ),
    )),
    ("DesignDbContainer", (
        ( "New Design"  , "NewDesign"  ),
        ( "Open Design" , "OpenDesign" )
    )),
    ("LibraryDbContainer", (
        ( "New Library"  , "NewLibrary"  ),
        ( "Open Library" , "OpenLibrary" )
    )),
    ("DesignDbNode", (
        ( "Save Design"           , "SaveDesign"          ),
        ( "Save Design As"        , "SaveDesignAs"        ),
        ( "Close Design"          , "CloseDesign"         ),
        "--",
        ( "Rename Design"         , "RenameDesign"        ),
        "--",
        ( "New Symbol"            , "NewSymbol"           ),
        "--",
        ( "Edit Diagram"          , "EditDiagram"         ),
        ( "New Diagram Window"    , "NewDiagramWindow"    ),
        "--",
        ( "Edit Properties"       , "EditProperties"      ),
        ( "New Properties Window" , "NewPropertiesWindow" )
    )),
    ("LibraryDbNode", (
        "--",
        ( "Save Library"    , "SaveLibrary"   ),
        ( "Save Library As" , "SaveLibraryAs" ),
        ( "Close Library"   , "CloseLibrary"  ),
        "--",
        ( "Rename Library"  , "RenameLibrary" ),
        "--",
        ( "New Symbol"      , "NewSymbol"     )
    )),
    ("SymbolNode", (
        ( "Edit Symbol"       , "EditSymbol"      ),
        ( "New Symbol Window" , "NewSymbolWindow" ),
        "--",
        ( "Rename Symbol"     , "RenameSymbol"    )
    ))
)

class NavigatorMenusMixin:

    # instance attributes
    menus : dict[str | None, Menu]

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
        self.newDiagram()

    def _slotOpenDesign(self : "Navigator") -> None:
        self.openDiagram()

    def _slotSaveDesign(self : "Navigator") -> None:
        self.save(self.node)

    def _slotSaveDesignAs(self : "Navigator") -> None:
        self.saveAs(self.node)

    def _slotCloseDesign(self : "Navigator") -> None:
        self.close(self.node)

    def _slotRenameDesign(self : "Navigator") -> None:
        self.rename(self.node)

    def _slotNewLibrary(self : "Navigator") -> None:
        self.newLibrary()

    def _slotOpenLibrary(self : "Navigator") -> None:
        self.openLibrary()

    def _slotSaveLibrary(self : "Navigator") -> None:
        self.save(self.node)

    def _slotSaveLibraryAs(self : "Navigator") -> None:
        self.saveAs(self.node)

    def _slotCloseLibrary(self : "Navigator") -> None:
        self.closeLibrary(self.node)

    def _slotRenameLibrary(self : "Navigator") -> None:
        self.rename(self.node)

    def _slotNewSymbol(self : "Navigator") -> None:
        self.newSymbol(self.node)

    def _slotEditSymbol(self : "Navigator") -> None:
        self.editDrawing(self.node)

    def _slotNewSymbolWindow(self : "Navigator") -> None:
        self.newSymbolWindow(self.node)

    def _slotRenameSymbol(self : "Navigator") -> None:
        self.rename(self.node)

    def _slotEditDiagram(self : "Navigator") -> None:
        self.editDrawing(self.node)

    def _slotNewDiagramWindow(self : "Navigator") -> None:
        self.newDrawingWindow(self.node)

    def _slotEditProperties(self : "Navigator") -> None:
        self.editProperties(self.node)

    def _slotNewPropertiesWindow(self : "Navigator") -> None:
        self.newPropertiesWindow(self.node)

    def _slotRename(self : "Navigator") -> None:
        self.rename(self.node)

    def _slotCopy(self : "Navigator") -> None:
        self.copy(self.node)

    def _slotPaste(self : "Navigator") -> None:
        self.paste(self.node)
