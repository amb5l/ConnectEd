from menus.menus import Menu

________________________________________________________ = [ "", None ],

CONTEXT_MENU = [
    [ "Cut"               , "editCut"              , False ],
    [ "Copy"              , "editCopy"             , False ],
    [ "Paste"             , "editPaste"            , False ],
    [ "Delete"            , "editDelete"           , False ],
    ________________________________________________________,
    [ 'Slide'             , 'editSlide'            , False ],
    [ 'Move'              , 'editMove'             , False ],
    [ "Mirror Horizontal" , "editMirrorHorizontal" , False ],
    [ "Mirror Vertical"   , "editMirrorVertical"   , False ],
    [ "Rotate"            , "editRotate"           , False ],
    [ "Lock"              , "editLock"             , False ],
    [ "Unlock"            , "editUnlock"           , False ],
    [ "Properties"        , "editProperties"       , False ],
    ________________________________________________________,
    [ "Zoom In"           , "viewZoomIn"           , False ],
    [ "Zoom Out"          , "viewZoomOut"          , False ],
    [ "Zoom Window"       , "viewZoomWindow"       , False ],
    [ "Zoom Full"         , "viewZoomFull"         , False ],
    ________________________________________________________,
    [ "Cancel"            , "editCancel"           , False ]
]

class CanvasMenu(Menu):
    def __init__(self, parent, actions):
        super().__init__(parent, "Canvas", CONTEXT_MENU, actions)

class CanvasMenuMixin:
    def contextMenuEvent(self, event):
        self.menu.exec(event.globalPos())
