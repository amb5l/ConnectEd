from PyQt6.QtGui import QKeySequence

menuShortcuts = {
    "&File"    : "Alt+F",
    "&Edit"    : "Alt+E",
    "&View"    : "Alt+V",
    "&Place"   : "Alt+P",
    "&Options" : "Alt+O",
    "&Help"    : "Alt+H"
}

actionShortcuts = {

    "fileNew"            : QKeySequence.StandardKey.Print     ,
    "fileOpen"           : QKeySequence.StandardKey.Open      ,
    "fileSave"           : QKeySequence.StandardKey.Save      ,
    "fileSaveAs"         : QKeySequence.StandardKey.SaveAs    ,
    "fileClose"          : QKeySequence.StandardKey.Close     ,
    "fileExport"         : None                               ,
    "fileImport"         : None                               ,
    "filePrint"          : QKeySequence.StandardKey.Print     ,
    "filePrintPreview"   : None                               ,
    "filePageSetup"      : None                               ,

    "editCancel"         : "Escape"                           ,
    "editUndo"           : QKeySequence.StandardKey.Undo      ,
    "editRedo"           : QKeySequence.StandardKey.Redo      ,
    "editRepeat"         : "F4"                               ,
    "editCut"            : QKeySequence.StandardKey.Cut       ,
    "editCopy"           : QKeySequence.StandardKey.Copy      ,
    "editPaste"          : QKeySequence.StandardKey.Paste     ,
    "editDelete"         : QKeySequence.StandardKey.Delete    ,
    "editSelectAll"      : QKeySequence.StandardKey.SelectAll ,
    "editFind"           : QKeySequence.StandardKey.Find      ,
    "editReplace"        : QKeySequence.StandardKey.Replace   ,
    "editSelectAll"      : QKeySequence.StandardKey.SelectAll ,
    "editSelectFilter"   : None                               ,

    "viewGrid"           : "G"                                ,
    "viewTransparent"    : "T"                                ,
    "viewOpaque"         : "O"                                ,
    "viewZoomIn"         : "PgUp"                             ,
    "viewZoomOut"        : "PgDown"                           ,
    "viewZoomWindow"     : "W"                                ,
    "viewZoomFull"       : "Home"                             ,
    "viewPanLeft"        : "Left"                             ,
    "viewPanRight"       : "Right"                            ,
    "viewPanUp"          : "Up"                               ,
    "viewPanDown"        : "Down"                             ,

    "placeBlock"         : "Ctrl+Alt+B"                        ,
    "placePin"           : "Ctrl+Alt+E"                        ,
    "placeWire"          : "Ctrl+Alt+W"                        ,
    "placeTap"           : "Ctrl+Alt+T"                        ,
    "placeJunction"      : "Ctrl+Alt+J"                        ,
    "placePort"          : "Ctrl+Alt+P"                        ,
    "placeConnection"    : "Ctrl+Alt+C"                        ,
    "placeProperty"      : "Ctrl+Alt+Y"                        ,
    "placeCode"          : "Ctrl+Alt+O"                        ,
    "placeLine"          : "Shift+Alt+L"                       ,
    "placeRectangle"     : "Shift+Alt+R"                       ,
    "placePolygon"       : "Shift+Alt+P"                       ,
    "placeArc"           : "Shift+Alt+A"                       ,
    "placeEllipse"       : "Shift+Alt+E"                       ,
    "placeTextLine"      : "Shift+Alt+T"                       ,
    "placeTextBox"       : "Shift+Alt+B"                       ,
    "placeImage"         : "Shift+Alt+I"                       ,

    "optionsThemes"      : None                               ,
    "optionsPreferences" : None                               ,
    "optionsShortcuts"   : None                               ,
    "optionsReset"       : None                               ,

    "helpAbout"          : "F1"
}
