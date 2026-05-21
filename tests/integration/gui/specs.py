"""GUI integration test data (menu trees, main-window shell)."""

from collections.abc import Callable
from typing import Any

from ConnectEd.scripting import (
    LogViewDock,
    MdiArea,
    MenuBar,
    MessagesViewDock,
    NavigatorDock,
    NetlistBrowserDock,
    StatusBar,
    TranscriptViewDock,
    Window,
)

MENUS_BASE : dict[str, list] = {
    "File" : [
        {"New" : ["Design", "Library"]},
        "Open",
        "Save",
        "Save As",
        "Close",
        "Exit",
    ],
    "Edit" : [
        "Cancel",
        "Undo",
        "Redo",
        "Cut",
        "Copy",
        "Paste",
        "Delete",
        "Duplicate",
        "Select Area",
        "Select All",
        "Properties",
        "Appearance",
        "Query",
    ],
    "View" : [
        {"Theme" : ["Dark", "Light Mono"]},
        "Zoom All",
        "Zoom Sheet",
        "Zoom Area",
        "Zoom In",
        "Zoom Out",
        "Pan",
        "Pan Up",
        "Pan Down",
        "Pan Left",
        "Pan Right",
        "Grid Display",
        "Grid Snap",
    ],
    "Window" : [
        "Next",
        "Previous",
        "Navigator",
        "Messages",
        "Transcript",
        "Log",
    ],
    "Help" : [
        "About",
    ],
}

PLACE_STARTUP : list[str] = []

PLACE_DIAGRAM : list[str] = [
    "Port",
    "Gate",
    "Block",
    "Block Pin",
    "Connection",
    "Tap",
    "Line",
    "Rectangle",
    "Ellipse",
    "Polyline",
    "Text",
]

MENUS_STARTUP : dict[str, list] = {**MENUS_BASE, "Place" : PLACE_STARTUP}

MAIN_WIDGETS : dict[str, tuple[type, Callable[[Window], Any]]] = {
    "menuBar"    : ( MenuBar            , lambda win : win.menuBar()        ),
    "statusBar"  : ( StatusBar          , lambda win : win.statusBar()      ),
    "central"    : ( MdiArea            , lambda win : win.mdiArea()        ),
    "Navigator"  : ( NavigatorDock      , lambda win : win.navigatorDock()  ),
    "Netlist"    : ( NetlistBrowserDock , lambda win : win.netlistDock()    ),
    "Messages"   : ( MessagesViewDock   , lambda win : win.messagesDock()   ),
    "Transcript" : ( TranscriptViewDock , lambda win : win.transcriptDock() ),
    "Log"        : ( LogViewDock        , lambda win : win.logDock()        )
}
