from PyQt6.QtGui import QKeySequence

from ...private import Action

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...main_window import MainWindow


class Actions:
    _parent : 'MainWindow'

    def __init__(self : 'Actions', parent : 'MainWindow') -> None:
        self._parent = parent
        SK = QKeySequence.StandardKey

        # submenu actions
        # TODO Zoom 100%/10% etc

        # menu actions
        self.fileExit       = Action( self._parent, 'Exit'        , 'Exit the application'     , SK.Quit        , False )
        self.viewZoomAll    = Action( self._parent, 'Zoom All'    , 'Zoom to fit all'          , 'Ctrl+Home'    , False )
        self.viewZoomSheet  = Action( self._parent, 'Zoom Sheet'  , 'Zoom to fit sheet'        , 'Ctrl+Shift+S' , False )
        self.viewZoomWindow = Action( self._parent, 'Zoom Window' , 'Zoom to window'           , 'Ctrl+Shift+W' , False )
        self.viewZoomIn     = Action( self._parent, 'Zoom In'     , 'Zoom in'                  , 'Ctrl++'       , False )
        self.viewZoomOut    = Action( self._parent, 'Zoom Out'    , 'Zoom out'                 , 'Ctrl+-'       , False )
        self.viewCenter     = Action( self._parent, 'Center'      , 'Center view'              , ''             , False )
        self.viewPan        = Action( self._parent, 'Pan'         , 'Pan view'                 , 'Ctrl+P'       , False )
        self.windowMessages = Action( self._parent, 'Messages'    , 'Show the messages window' , 'Ctrl+Shift+M' , False )
        self.windowLog      = Action( self._parent, 'Log'         , 'Show the log window'      , 'Ctrl+Shift+L' , False )
        self.helpAbout      = Action( self._parent, 'About'       , ''                         , 'Ctrl+Shift+T' , False )

    def actionEnable(self, name : str, enable : bool) -> None:
        getattr(self, name).setEnabled(enable)
