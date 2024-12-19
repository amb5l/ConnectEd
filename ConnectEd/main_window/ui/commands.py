from enum import Flag, auto
from dataclasses import dataclass
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QMessageBox

from common import logger
from settings import prefs
from .slots import Slots


class CmdFlags(Flag):
    NONE             = 0
    DIAGRAM_EXISTS   = auto()
    ITEMS_SELECTED   = auto()
    VIEW_PREV_EXISTS = auto()
    VIEW_NEXT_EXISTS = auto()
    ZOOM_GT_MIN      = auto() # zoom greater than min e.g. viewZoomOut
    ZOOM_LT_MAX      = auto() # zoom less than max e.g. viewZoomIn

@dataclass
class CmdDef():
    text      : str          # text to display on menu item
    shortcut  : QKeySequence # shortcut key sequence
    checkable : bool         # whether the action is checkable
    flags     : CmdFlags     # flags to enable/disable action

SK = QKeySequence.StandardKey
CMD_DEFS = {
    'fileNew'         : CmdDef( 'New'        , SK.New                , False , CmdFlags.NONE                                       ),
    'fileOpen'        : CmdDef( 'Open'       , SK.Open               , False , CmdFlags.NONE                                       ),
    'fileSave'        : CmdDef( 'Save'       , SK.Save               , False , CmdFlags.NONE                                       ),
    'fileSaveAs'      : CmdDef( 'Save As'    , SK.SaveAs             , False , CmdFlags.NONE                                       ),
    'fileClose'       : CmdDef( 'Close'      , SK.Close              , False , CmdFlags.NONE                                       ),
    'viewZoomAll'     : CmdDef( 'Zoom All'   , 'Home'                , False , CmdFlags.DIAGRAM_EXISTS                             ),
    'viewZoomSheet'   : CmdDef( 'Zoom Sheet' , 'Ctrl+Home'           , False , CmdFlags.DIAGRAM_EXISTS                             ),
    'viewZoomExtents' : CmdDef( 'Zoom Full'  , 'Alt+Home'            , False , CmdFlags.DIAGRAM_EXISTS                             ),
    'viewZoomIn'      : CmdDef( 'Zoom In'    , SK.ZoomIn             , False , CmdFlags.DIAGRAM_EXISTS | CmdFlags.ZOOM_LT_MAX      ),
    'viewZoomOut'     : CmdDef( 'Zoom Out'   , SK.ZoomOut            , False , CmdFlags.DIAGRAM_EXISTS | CmdFlags.ZOOM_GT_MIN      ),
    'viewPanLeft'     : CmdDef( 'Pan Left'   , SK.MoveToPreviousChar , False , CmdFlags.DIAGRAM_EXISTS                             ),
    'viewPanRight'    : CmdDef( 'Pan Right'  , SK.MoveToNextChar     , False , CmdFlags.DIAGRAM_EXISTS                             ),
    'viewPanUp'       : CmdDef( 'Pan Up'     , SK.MoveToPreviousLine , False , CmdFlags.DIAGRAM_EXISTS                             ),
    'viewPanDown'     : CmdDef( 'Pan Down'   , SK.MoveToNextLine     , False , CmdFlags.DIAGRAM_EXISTS                             ),
    'viewPrev'        : CmdDef( 'Previous'   , SK.Back               , False , CmdFlags.DIAGRAM_EXISTS | CmdFlags.VIEW_PREV_EXISTS ),
    'viewNext'        : CmdDef( 'Next'       , SK.Forward            , False , CmdFlags.DIAGRAM_EXISTS | CmdFlags.VIEW_NEXT_EXISTS ),
    'helpAbout'       : CmdDef( 'About'      , SK.HelpContents       , False , CmdFlags.NONE                                       )
}

class Action(QAction):
    def __init__(self, text, shortcut, checkable, flags):
        super().__init__()
        self.setText(text)
        self.setShortcut(shortcut)
        self.setCheckable(checkable)
        self.flags = flags

    def getFlags(self):
        return self.flags

class Commands:
    def __init__(self, parent):
        self.parent = parent
        self.slots = Slots(self)
        self.actions = {}

    def build(self):
        for name, cmd_def in CMD_DEFS.items():
            text = cmd_def.text
            shortcut = cmd_def.shortcut
            checkable = cmd_def.checkable
            flags = cmd_def.flags
            if isinstance(shortcut, str):
                shortcut = QKeySequence(shortcut)
            # create action
            action = Action(text, shortcut, checkable, flags)
            # connect action to slot
            if hasattr(self.slots, name):
                action.triggered.connect(getattr(self.slots, name))
                logger.info(f'slot connected for command: {name}')
            else:
                action.triggered.connect(self.slotMissing)
                logger.warning(f'slot missing for command: {name}')
            self.actions[name] = action

    def slotMissing(self):
        action = self.sender()
        action_name = action.objectName()
        QMessageBox.warning(self.parent, 'Warning', f'No slot connected to action: {action_name}')

    def update(self):
        flags = CmdFlags.NONE
        diagram = self.parent.diagram
        canvas = self.parent.canvas
        if diagram.data:
            flags |= CmdFlags.DIAGRAM_EXISTS
        if diagram.selected:
            flags |= CmdFlags.ITEMS_SELECTED
        if canvas.zoom > prefs.display.zoom.min:
            flags |= CmdFlags.ZOOM_GT_MIN
        if canvas.zoom < prefs.display.zoom.max:
            flags |= CmdFlags.ZOOM_LT_MAX
        for action in self.actions.__dict__.values():
            action.setEnabled(flags & action.getFlags() == action.getFlags())
