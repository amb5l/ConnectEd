from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction, QActionGroup

from common import logger
from .shortcuts import actionShortcuts


class MenuDef:
    def __init__(self, name, items):
        self.name  = name
        self.items = items

class ActionGroupDef:
    def __init__(self, items):
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
        ActionDef(              'Previous'           , 'viewPrev'             , False ),
        ActionDef(              'Next'               , 'viewNext'             , False ),
        SeparatorDef(),         #-------------------------------------------------------
        ActionDef(              'Zoom In'            , 'viewZoomIn'           , False ),
        ActionDef(              'Zoom Out'           , 'viewZoomOut'          , False ),
        ActionDef(              'Zoom Window'        , 'viewZoomWindow'       , False ),
        ActionDef(              'Zoom Full'          , 'viewZoomFull'         , False ),
        ActionDef(              'Zoom Selected'      , 'viewZoomSelected'     , False ),
        SeparatorDef(),         #-------------------------------------------------------
        ActionDef(              'Pan Left'           , 'viewPanLeft'          , False ),
        ActionDef(              'Pan Right'          , 'viewPanRight'         , False ),
        ActionDef(              'Pan Up'             , 'viewPanUp'            , False ),
        ActionDef(              'Pan Down'           , 'viewPanDown'          , False )
        SeparatorDef(),         #-------------------------------------------------------
        ActionDef(              'Grid'               , 'viewGrid'             , True  ),
        ActionDef(              'Transparent'        , 'viewTransparent'      , True  ),
        ActionDef(              'Opaque'             , 'viewOpaque'           , True  ),
        SeparatorDef(),         #-------------------------------------------------------
        ActionDef(              'Normal'             , 'viewNormal'           , True  ),
        ActionDef(              'Rotated'            , 'viewRotated'          , True  )
    ]),
                            #===========================================================
    MenuDef(                'Place', [
        ActionDef(              'Block'              , 'elementBlock'         , True  ),
        ActionDef(              'Pin'                , 'elementPin'           , True  ),
        ActionDef(              'Wire'               , 'elementWire'          , True  ),
        ActionDef(              'Tap'                , 'elementTap'           , True  ),
        ActionDef(              'Junction'           , 'elementJunction'      , True  ),
        ActionDef(              'Port'               , 'elementPort'          , True  ),
        ActionDef(              'Code'               , 'elementCode'          , True  ),
        SeparatorDef(),         #-------------------------------------------------------
        ActionDef(              'Line'               , 'decorationLine'       , True  ),
        ActionDef(              'Rectangle'          , 'decorationRectangle'  , True  ),
        ActionDef(              'Polygon'            , 'decorationPolygon'    , True  ),
        ActionDef(              'Arc'                , 'decorationArc'        , True  ),
        ActionDef(              'Ellipse'            , 'decorationEllipse'    , True  ),
        ActionDef(              'Text Line'          , 'decorationTextLine'   , True  ),
        ActionDef(              'Text Box'           , 'decorationTextBox'    , True  ),
        ActionDef(              'Image...'           , 'decorationImage'      , True  )
    ]),
                            #===========================================================
    MenuDef(                'Options', [
        ActionDef(              'Diagram...'         , 'optionsDiagram'       , False ),
        ActionDef(              'Themes...'          , 'optionsThemes'        , False ),
        ActionDef(              'Preferences...'     , 'optionsPreferences'   , False ),
        ActionDef(              'Shortcuts...'       , 'optionsShortcuts'     , False ),
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
    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.menusDict = {}
        for menuDef in MENUS:
            menu = Menu(mainWindow, '&' + menuDef.name, menuDef.items)
            self.menusDict[menuDef.name] = menu
            self.addMenu(menu)

class Menu(QMenu):
    def __init__(self, mainWindow, name, itemDefs):
        super().__init__(name, mainWindow)
        self.itemsDict = {}
        print('Menu:', name)
        for itemDef in itemDefs:
            if isinstance(itemDef, MenuDef):
                print('  Menu:', itemDef.name)
                item = Menu(mainWindow, itemDef.name, itemDef.items)
                self.addMenu(item)
                self.itemsDict[itemDef.name] = item
            elif isinstance(itemDef, ActionGroupDef):
                print('  ActionGroup:')
                item = ActionGroup(mainWindow, self, itemDef.items)
            elif isinstance(itemDef, ActionDef):
                print('  Action:', itemDef.text)
                item = Action(mainWindow, itemDef.text, itemDef.name, itemDef.checkable)
                self.addAction(item)
                self.itemsDict[itemDef.name] = item
            elif isinstance(itemDef, SeparatorDef):
                print('  Separator')
                item = QAction(mainWindow)
                item.setSeparator(True)
            else:
                logger.error(f'Menu: bad itemDef type: {type(itemDef)}')

class ActionGroup(QActionGroup):
    def __init__(self, mainWindow, menu, itemDefs):
        super().__init__(mainWindow)
        self.itemsDict = {}
        for itemDef in itemDefs:
            if isinstance(itemDef, ActionDef):
                item = Action(mainWindow, itemDef.text, itemDef.name, itemDef.checkable)
                menu.itemsDict[itemDef.name] = item
            elif isinstance(itemDef, SeparatorDef):
                item = QAction(mainWindow)
                item.setSeparator(True)
            else:
                logger.error(f'ActionGroup: bad itemDef type: {type(itemDef)}')
                continue
            menu.addAction(item)

class Action(QAction):
    def __init__(self, mainWindow, text, name, checkable):
        def ActionFunction(name): # looks up and returns action method by name
            return lambda checked=False, x=name: getattr(mainWindow.actions, x)()
        super().__init__(text, mainWindow)
        self.setCheckable(checkable)
        self.triggered.connect(ActionFunction(name))
        if name in actionShortcuts:
            if actionShortcuts[name] is not None:
                self.setShortcut(actionShortcuts[name])
