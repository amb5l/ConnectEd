from enum import Flag, auto
from dataclasses import dataclass
from types import SimpleNamespace
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QMessageBox
SK = QKeySequence.StandardKey

from common import logger
from settings import prefs

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
    inst      : str          # name of instance that contains the slot function ('diagram' or 'canvas')
    text      : str          # text to display on menu item
    shortcut  : QKeySequence # shortcut key sequence
    checkable : bool         # whether the action is checkable
    flags     : CmdFlags     # flags to enable/disable action

CMD_DEFS = {

    'fileNew'         : CmdDef( 'diagram' , 'New'        , SK.New                , False , CmdFlags.NONE                                       ),
    'fileOpen'        : CmdDef( 'diagram' , 'Open'       , SK.Open               , False , CmdFlags.NONE                                       ),
    'fileSave'        : CmdDef( 'diagram' , 'Save'       , SK.Save               , False , CmdFlags.NONE                                       ),
    'fileSaveAs'      : CmdDef( 'diagram' , 'Save As'    , SK.SaveAs             , False , CmdFlags.NONE                                       ),
    'fileClose'       : CmdDef( 'diagram' , 'Close'      , SK.Close              , False , CmdFlags.NONE                                       ),

    'viewZoomAll'     : CmdDef( 'canvas'  , 'Zoom All'   , 'Home'                , False , CmdFlags.DIAGRAM_EXISTS                             ),
    'viewZoomSheet'   : CmdDef( 'canvas'  , 'Zoom Sheet' , 'Ctrl+Home'           , False , CmdFlags.DIAGRAM_EXISTS                             ),
    'viewZoomExtents' : CmdDef( 'canvas'  , 'Zoom Full'  , 'Alt+Home'            , False , CmdFlags.DIAGRAM_EXISTS                             ),
    'viewZoomIn'      : CmdDef( 'canvas'  , 'Zoom In'    , SK.ZoomIn             , False , CmdFlags.DIAGRAM_EXISTS | CmdFlags.ZOOM_LT_MAX      ),
    'viewZoomOut'     : CmdDef( 'canvas'  , 'Zoom Out'   , SK.ZoomOut            , False , CmdFlags.DIAGRAM_EXISTS | CmdFlags.ZOOM_GT_MIN      ),
    'viewPanLeft'     : CmdDef( 'canvas'  , 'Pan Left'   , SK.MoveToPreviousChar , False , CmdFlags.DIAGRAM_EXISTS                             ),
    'viewPanRight'    : CmdDef( 'canvas'  , 'Pan Right'  , SK.MoveToNextChar     , False , CmdFlags.DIAGRAM_EXISTS                             ),
    'viewPanUp'       : CmdDef( 'canvas'  , 'Pan Up'     , SK.MoveToPreviousLine , False , CmdFlags.DIAGRAM_EXISTS                             ),
    'viewPanDown'     : CmdDef( 'canvas'  , 'Pan Down'   , SK.MoveToNextLine     , False , CmdFlags.DIAGRAM_EXISTS                             ),
    'viewPrev'        : CmdDef( 'canvas'  , 'Previous'   , SK.Back               , False , CmdFlags.DIAGRAM_EXISTS | CmdFlags.VIEW_PREV_EXISTS ),
    'viewNext'        : CmdDef( 'canvas'  , 'Next'       , SK.Forward            , False , CmdFlags.DIAGRAM_EXISTS | CmdFlags.VIEW_NEXT_EXISTS ),

    'helpAbout'       : CmdDef( 'diagram' , 'About'      , SK.HelpContents , False , CmdFlags.NONE                                             )

}

class Action(QAction):
    def __init__(self, shortcut, flags):
        super().__init__()
        self.setText('undefined')
        self.setShortcut(shortcut)
        self.flags = flags

    def getFlags(self):
        return self.flags

'''
Builds and contains QAction instances for all commands.
'''
class Commands:
    def __init__(self, window):
        self.window = window
        self.actions = SimpleNamespace()
        for name, cmd_def in CMD_DEFS.items():
            logger.info(f'creating command: {name}')
            inst = self.window.canvas if cmd_def.inst == 'canvas' else self.window.canvas.diagram
            text = cmd_def.text
            shortcut = cmd_def.shortcut
            checkable = cmd_def.checkable
            if isinstance(shortcut, str):
                shortcut = QKeySequence(shortcut)
            flags = cmd_def.flags
            action = Action(shortcut, flags)
            action.setText(text)
            action.setCheckable(checkable)
            if hasattr(inst.slots, name):
                action.triggered.connect(getattr(inst.slots, name))
            else:
                action.triggered.connect(self.slotMissing)
            setattr(self.actions, name, action)

    def slotMissing(self):
        action = self.sender()
        action_name = action.objectName()
        QMessageBox.warning(self.window, 'Warning', f'No slot connected to action: {action_name}')

    def update(self):
        flags = CmdFlags.NONE
        if self.diagram.data:
            flags |= CmdFlags.DIAGRAM_EXISTS
        if self.diagram.selected:
            flags |= CmdFlags.ITEMS_SELECTED
        if self.canvas.zoom > prefs.display.zoom.min:
            flags |= CmdFlags.ZOOM_GT_MIN
        if self.canvas.zoom < prefs.display.zoom.max:
            flags |= CmdFlags.ZOOM_LT_MAX
        for action in self.actions.__dict__.values():
            action.setEnabled(flags & action.getFlags() == action.getFlags())