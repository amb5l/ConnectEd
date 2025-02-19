from dataclasses import dataclass

from PyQt6.QtGui import QKeySequence, QAction

from ....core.types import Action

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....widgets.main_window import MainWindow

#@dataclass
class Actions:
    _parent : 'MainWindow'

    def __init__(self : 'Actions', parent : 'MainWindow'):
        self._parent = parent
        SK = QKeySequence.StandardKey
        self.fileExit            = Action( self._parent, 'Exit'            , 'Exit the application'                                    , SK.Quit               , False )
        self.helpAbout           = Action( self._parent, 'About'           , ''                                                        , 'Ctrl+Shift+T'        , False )
