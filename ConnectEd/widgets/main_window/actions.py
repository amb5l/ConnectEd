from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence

from ..private import Action

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..main_window import MainWindow


class Actions:
    _parent : 'MainWindow'

    def __init__(self : 'Actions', parent : 'MainWindow') -> None:
        self._parent = parent
        SK = QKeySequence.StandardKey

        self.fileExit        = Action( self._parent, 'Exit'        , 'Exit the application'        , SK.Quit                         )
        self.editCancel      = Action( self._parent, 'Cancel'      , 'Cancel the current action'   , SK.Cancel                       )
        self.editComplete    = Action( self._parent, 'Complete'    , 'Complete the current action' , QKeySequence(Qt.Key.Key_Return) )
        self.editSlide       = Action( self._parent, 'Slide'       , 'Slide'                       , ''                              )
        self.editMove        = Action( self._parent, 'Move'        , 'Move'                        , ''                              )
        self.viewZoomAll     = Action( self._parent, 'Zoom All'    , 'Zoom to fit all'             , 'Ctrl+Home'                     )
        self.viewZoomSheet   = Action( self._parent, 'Zoom Sheet'  , 'Zoom to fit sheet'           , 'Ctrl+Shift+S'                  )
        self.viewZoomWindow  = Action( self._parent, 'Zoom Window' , 'Zoom to window'              , 'Ctrl+Shift+W'                  )
        self.viewZoomIn      = Action( self._parent, 'Zoom In'     , 'Zoom in'                     , 'Ctrl++'                        )
        self.viewZoomOut     = Action( self._parent, 'Zoom Out'    , 'Zoom out'                    , 'Ctrl+-'                        )
        self.viewPan         = Action( self._parent, 'Pan'         , 'Pan'                         , ''                              )
        self.viewPanUp       = Action( self._parent, 'Pan Up'      , 'Pan up'                      , 'Ctrl+Up'                       )
        self.viewPanDown     = Action( self._parent, 'Pan Down'    , 'Pan down'                    , 'Ctrl+Down'                     )
        self.viewPanLeft     = Action( self._parent, 'Pan Left'    , 'Pan left'                    , 'Ctrl+Left'                     )
        self.viewPanRight    = Action( self._parent, 'Pan Right'   , 'Pan right'                   , 'Ctrl+Right'                    )
        self.viewGridDisplay = Action( self._parent, 'Grid Display', 'Toggle grid display'         , 'Ctrl+G'       , True , True    )
        self.viewGridSnap    = Action( self._parent, 'Grid Snap'   , 'Toggle grid snap'            , 'Ctrl+Shift+G' , True , True    )
        self.placeRectangle  = Action( self._parent, 'Rectangle'   , 'Place Rectangle'             , 'Ctrl+R'                        )
        self.windowMessages  = Action( self._parent, 'Messages'    , 'Show the messages window'    , 'Ctrl+Shift+M'                  )
        self.windowLog       = Action( self._parent, 'Log'         , 'Show the log window'         , 'Ctrl+Shift+L'                  )
        self.helpAbout       = Action( self._parent, 'About'       , ''                            , 'Ctrl+Shift+T'                  )

    def actionEnable(self, name : str, enable : bool) -> None:
        getattr(self, name).setEnabled(enable)
