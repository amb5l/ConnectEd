from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction, QActionGroup

from common import logger
from shortcuts import actionShortcuts


class MenuDef:
    def __init__(self, name, items):
        self.name  = name
        self.items = items

class ActionGroupDef:
    def __init__(self, name, items):
        self.name  = name
        self.items = items

class ActionDef:
    def __init__(self, text, name, checkable):
        self.text      = text
        self.name      = name
        self.checkable = checkable

class SeparatorDef:
    pass

MENUS = [
                            #===========================================================
    MenuDef(                'File', [
        ActionDef(              'New'                , 'fileNew'              , False ),
        ActionDef(              'Open'               , 'fileOpen'             , False ),
        ActionDef(              'Save'               , 'fileSave'             , False ),
        ActionDef(              'Save As...'         , 'fileSaveAs'           , False ),
        ActionDef(              'Close'              , 'fileClose'            , False ),
        SeparatorDef(),         #-------------------------------------------------------
        MenuDef(                'Export', [
            ActionDef(              'VHDL'           , 'fileExportVHDL'       , False ),
            ActionDef(              'Verilog'        , 'fileExportVerilog'    , False ),
            ActionDef(              'PDF'            , 'fileExportPDF'        , False ),
            ActionDef(              'SVG'            , 'fileExportSVG'        , False )
        ]),
        MenuDef(                'Import', [
            ActionDef(              'VHDL'           , 'fileImportVHDL'       , False ),
            ActionDef(              'Verilog'        , 'fileImportVerilog'    , False )
        ]),
        SeparatorDef(),         #-------------------------------------------------------
        ActionDef(              'Print'              , 'filePrint'            , False ),
        ActionDef(              'Print Preview'      , 'filePrintPreview'     , False ),
        ActionDef(              'Page Setup'         , 'filePageSetup'        , False )
    ]),
                            #===========================================================
    MenuDef(                'Edit', [
        ActionDef(              'Cancel'             , 'editCancel'           , False ),
        ActionDef(              'Undo'               , 'editUndo'             , False ),
        ActionDef(              'Redo'               , 'editRedo'             , False ),
        ActionDef(              'Repeat'             , 'editRepeat'           , False ),
        SeparatorDef(),         #-------------------------------------------------------
        ActionDef(              'Select All'         , 'editSelectAll'        , False ),
        ActionDef(              'Select Window'      , 'editSelectWindow'     , False ),
        ActionDef(              'Select Filter...'   , 'editSelectFilter'     , False ),
        SeparatorDef(),         #-------------------------------------------------------
        ActionDef(              'Cut'                , 'editCut'              , False ),
        ActionDef(              'Copy'               , 'editCopy'             , False ),
        ActionDef(              'Paste'              , 'editPaste'            , False ),
        ActionDef(              'Delete'             , 'editDelete'           , False ),
        SeparatorDef(),         #-------------------------------------------------------
        MenuDef(                'Transform', [
            ActionDef(              'Slide'          , 'editSlide'            , False ),
            ActionDef(              'Move'           , 'editMove'             , False ),
            MenuDef(                'Mirror', [
                ActionDef(              'Horizontal' , 'editMirrorHorizontal' , False ),
                ActionDef(              'Vertical'   , 'editMirrorVertical'   , False ),
                ActionDef(              'Both'       , 'editMirrorBoth'       , False )
            ]),
            ActionDef(              'Rotate'         , 'editRotate'           , False ),
            ActionDef(              'Align'          , 'editAlign'            , False )
        ]),
        ActionDef(              'Lock'               , 'editLock'             , False ),
        ActionDef(              'Unlock'             , 'editUnlock'           , False ),
        ActionDef(              'Fix'                , 'editFix'              , False ),
        ActionDef(              'Unfix'              , 'editUnfix'            , False ),
        ActionDef(              'Properties...'      , 'editProperties'       , False ),
        SeparatorDef(),         #-------------------------------------------------------
        ActionDef(              'Find'               , 'editFind'             , False ),
        ActionDef(              'Replace'            , 'editReplace'          , False ),
        SeparatorDef(),         #-------------------------------------------------------
        ActionDef(              'Snap to Grid'       , 'editSnap'             , True  )
    ]),
                            #===========================================================
    MenuDef(                'View', [
        ActionDef(              'Grid'               , 'viewGrid'             , True  ),
        ActionDef(              'Transparent'        , 'viewTransparent'      , True  ),
        ActionDef(              'Opaque'             , 'viewOpaque'           , True  ),
        SeparatorDef(),         #-------------------------------------------------------
        ActionDef(              'Zoom In'            , 'viewZoomIn'           , False ),
        ActionDef(              'Zoom Out'           , 'viewZoomOut'          , False ),
        ActionDef(              'Zoom Window'        , 'viewZoomWindow'       , False ),
        ActionDef(              'Zoom Full'          , 'viewZoomFull'         , False ),
        SeparatorDef(),         #-------------------------------------------------------
        ActionDef(              'Pan Left'           , 'viewPanLeft'          , False ),
        ActionDef(              'Pan Right'          , 'viewPanRight'         , False ),
        ActionDef(              'Pan Up'             , 'viewPanUp'            , False ),
        ActionDef(              'Pan Down'           , 'viewPanDown'          , False )
    ]),
                            #===========================================================
    MenuDef(                'Place', [
        ActionGroupDef( 'Function', [
        ActionDef(              'Block'              , 'elementBlock'         , True  ),
        ActionDef(              'Pin'                , 'elementPin'           , True  ),
        ActionDef(              'Wire'               , 'elementWire'          , True  ),
        ActionDef(              'Tap'                , 'elementTap'           , True  ),
        ActionDef(              'Junction'           , 'elementJunction'      , True  ),
        ActionDef(              'Port'               , 'elementPort'          , True  ),
        ActionDef(              'Code'               , 'elementCode'          , True  ),
        ]),
        SeparatorDef(),         #-------------------------------------------------------
        ActionGroupDef( 'Decoration', [
        ActionDef(              'Line'               , 'decorationLine'       , True  ),
        ActionDef(              'Rectangle'          , 'decorationRectangle'  , True  ),
        ActionDef(              'Polygon'            , 'decorationPolygon'    , True  ),
        ActionDef(              'Arc'                , 'decorationArc'        , True  ),
        ActionDef(              'Ellipse'            , 'decorationEllipse'    , True  ),
        ActionDef(              'Text Line'          , 'decorationTextLine'   , True  ),
        ActionDef(              'Text Box'           , 'decorationTextBox'    , True  ),
        ActionDef(              'Image...'           , 'decorationImage'      , True  )
        ])
    ]),
                            #===========================================================
    MenuDef(                'Options', [
        ActionDef(              'Themes'             , 'optionsThemes'        , False ),
        ActionDef(              'Preferences'        , 'optionsPreferences'   , False ),
        ActionDef(              'Shortcuts'          , 'optionsShortcuts'     , False ),
        SeparatorDef(),         #-------------------------------------------------------
        ActionDef(              'Reset'              , 'optionsReset'         , False )
    ]),
                            #===========================================================
    MenuDef(                'Help', [
        ActionDef(                  'About'          , 'helpAbout'            , False )
    ])
                            #===========================================================
]

class MenuBar(QMenuBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.menus = {}
        for menuDef in MENUS:
            menu = Menu(parent, '&' + menuDef.name, menuDef.items)
            self.menus[menuDef.name] = menu
            parent.addMenu(menu)

class Menu(QMenu):
    def __init__(self, parent, name, itemDefs):
        def ActionFunction(name): # looks up and returns action method by name
            return lambda checked=False, x=name: getattr(parent.actions, x)()
        super().__init__(name, parent)
        self.items = {}
        for itemDef in itemDefs:
            if isinstance(itemDef, MenuDef):
                item = Menu(parent, itemDef.name, itemDef.items)
            elif isinstance(itemDef, ActionGroupDef):
                item = ActionGroup(parent, itemDef.name, itemDef.items)
            elif isinstance(itemDef, ActionDef):
                item = Action(parent, itemDef.text, itemDef.name, itemDef.checkable)
            elif isinstance(itemDef, SeparatorDef):
                item = QAction(parent)
                item.setSeparator(True)
            else:
                logger.error(f'Menu: bad itemDef type: {type(itemDef)}')
                continue
            self.items[itemDef.name] = item
            self.addAction(item)

class ActionGroup(QActionGroup):
    def __init__(self, parent, name, itemDefs):
        super().__init__(parent)
        self.items = {}
        for itemDef in itemDefs:
            if isinstance(itemDef, ActionDef):
                item = Action(parent, itemDef.text, itemDef.name, itemDef.checkable)
            elif isinstance(itemDef, SeparatorDef):
                item = QAction(parent)
                item.setSeparator(True)
            else:
                logger.error(f'ActionGroup: bad itemDef type: {type(itemDef)}')
                continue
            self.items[itemDef.name] = item
            self.addAction(item)

class Action(QAction):
    def __init__(self, parent, text, name, checkable):
        def ActionFunction(name): # looks up and returns action method by name
            return lambda checked=False, x=name: getattr(parent.actions, x)()
        super().__init__(text, parent)
        self.setCheckable(checkable)
        self.triggered.connect(ActionFunction(name))
