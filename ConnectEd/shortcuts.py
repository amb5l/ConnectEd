from PyQt6.QtGui import QKeySequence

class Shortcuts:
    fileNew            = QKeySequence.StandardKey.Print
    fileOpen           = QKeySequence.StandardKey.Open
    fileSave           = QKeySequence.StandardKey.Save
    fileSaveAs         = QKeySequence.StandardKey.SaveAs
    fileClose          = QKeySequence.StandardKey.Close
    fileExport         = None
    fileImport         = None
    filePrint          = QKeySequence.StandardKey.Print
    filePrintPreview   = None
    filePageSetup      = None
    editCancel         = "Escape"
    editUndo           = QKeySequence.StandardKey.Undo
    editRedo           = QKeySequence.StandardKey.Redo
    editCut            = QKeySequence.StandardKey.Cut
    editCopy           = QKeySequence.StandardKey.Copy
    editPaste          = QKeySequence.StandardKey.Paste
    editDelete         = QKeySequence.StandardKey.Delete
    editSelectAll      = QKeySequence.StandardKey.SelectAll
    editFind           = QKeySequence.StandardKey.Find
    editReplace        = QKeySequence.StandardKey.Replace
    editSelectAll      = QKeySequence.StandardKey.SelectAll
    editSelectFilter   = "Alt+F"
    elementBlock       = "Alt+B"
    elementPin         = "Alt+E"
    elementWire        = "Alt+W"
    elementTap         = "Alt+T"
    elementJunction    = "Alt+J"
    elementPort        = "Alt+P"
    elementConnection  = "Alt+C"
    elementProperty    = "Alt+Y"
    elementCode        = "Alt+O"
    graphicLine        = "Ctrl+Alt+L"
    graphicRectangle   = "Ctrl+Alt+R"
    graphicPolygon     = "Ctrl+Alt+P"
    graphicArc         = "Ctrl+Alt+A"
    graphicEllipse     = "Ctrl+Alt+E"
    graphicImage       = "Ctrl+Alt+I"
    graphicTextLine    = "Ctrl+Alt+T"
    graphicTextBox     = "Ctrl+Alt+B"
    viewZoomIn         = "PgUp"
    viewZoomOut        = "PgDown"
    viewZoomWindow     = "W"
    viewZoomFull       = "Home"
    viewPanLeft        = "Left"
    viewPanRight       = "Right"
    viewPanUp          = "Up"
    viewPanDown        = "Down"
    optionsPreferences = None
    helpAbout          = "F1"

shortcuts = Shortcuts()