# menu bar for main main_window

from dataclasses import dataclass, field
from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction, QActionGroup

from common import logger


@dataclass
class MenuDef:
    name  : str
    items : list

@dataclass
class ItemGroupDef:
    items : list

@dataclass
class ItemDef:
    item : str

class SeparatorDef:
    pass

class Separator(QAction):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSeparator(True)

MENU_DEFS = [
             #===========================================================
    MenuDef( 'File', [
        ItemDef( 'fileNew'           ),
        ItemDef( 'fileOpen'          ),
        ItemDef( 'fileSave'          ),
        ItemDef( 'fileSaveAs'        ),
        ItemDef( 'fileClose'         )
    ]),      #===========================================================
    MenuDef( 'Edit', [
        ItemDef( 'editUndo'          ),
        ItemDef( 'editRedo'          ),
        SeparatorDef(),
        ItemDef( 'editCut'           ),
        ItemDef( 'editCopy'          ),
        ItemDef( 'editPaste'         ),
    ]),      #===========================================================
    MenuDef( 'View', [
        ItemDef( 'viewZoomAll'       ),
        ItemDef( 'viewZoomSheet'     ),
        ItemDef( 'viewZoomSelection' ),
        ItemDef( 'viewZoomIn'        ),
        ItemDef( 'viewZoomOut'       ),
        SeparatorDef(),
        ItemDef( 'viewPanLeft'       ),
        ItemDef( 'viewPanRight'      ),
        ItemDef( 'viewPanUp'         ),
        ItemDef( 'viewPanDown'       ),
        SeparatorDef(),
        ItemDef( 'viewPrev'          ),
        ItemDef( 'viewNext'          )
    ]),      #===========================================================
    MenuDef( 'Help', [
        ItemDef( 'helpAbout'  )
    ])       #===========================================================
]

class MenuBar(QMenuBar):
    def __init__(self, main_window):
        logger.info('entry')
        super().__init__(main_window)
        for menu_def in MENU_DEFS:
            menu = Menu(main_window, '&' + menu_def.name, menu_def.items)
            self.addMenu(menu)

class Menu(QMenu):
    def __init__(self, main_window, name, item_defs):
        logger.info(f'building menu: {name}')
        super().__init__(name, main_window)
        for item_def in item_defs:
            if isinstance(item_def, MenuDef):
                logger.info(f'adding menu: {item_def.item}')
                self.addMenu(Menu(main_window, item_def.item, item_def.items))
            elif isinstance(item_def, ItemGroupDef):
                logger.info(f'adding action group: {item_def.item}')
                self.addMenu(ActionGroup(main_window, item_def.items))
            elif isinstance(item_def, ItemDef):
                logger.info(f'adding action: {item_def.item}')
                if hasattr(main_window.commands.actions, item_def.item):
                    self.addAction(getattr(main_window.commands.actions, item_def.item))
                else:
                    logger.error(f'action not found: {item_def.item}')
            elif isinstance(item_def, SeparatorDef):
                logger.info(f'adding separator')
                self.addAction(Separator(main_window))
            else:
                logger.error(f'Menu: bad itemDef type: {type(item_def)}')

class ActionGroup(QActionGroup):
    def __init__(self, main_window, item_defs):
        super().__init__(main_window)
        for item_def in item_defs:
            if isinstance(item_def, ItemDef):
                if hasattr(main_window.commands, item_def.item):
                    item = getattr(main_window.commands, item_def.item)
                    item.setText(item_def.text)
                    self.addAction(item)
                else:
                    logger.error(f'action not found: {item_def.item}')
            elif isinstance(item_def, SeparatorDef):
                item = QAction(self)
                item.setSeparator(True)
            else:
                logger.error(f'ActionGroup: bad itemDef type: {type(item_def)}')
                continue
