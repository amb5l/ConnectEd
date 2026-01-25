from collections.abc import Callable

from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QContextMenuEvent, QAction, QKeySequence, QIcon

from .....core.xml import paste

from ....menu import Menu

from ...items.grip import GripItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingView


class DrawingViewMenuMixin:
    def contextMenuEvent(self : "DrawingView", event : QContextMenuEvent) -> None:
        from ...items.mixin.menu import ItemMenuMixin
        vpos = event.pos()
        spos = self.mapToScene(vpos)
        menu = Menu()
        def _extendMenu(menu_items : list[QAction | QMenu]) -> None:
            if menu_items:
                for menu_item in menu_items:
                    if isinstance(menu_item, QAction):
                        menu.addAction(menu_item)
                    elif isinstance(menu_item, QMenu):
                        menu.addMenu(menu_item)
                menu.addSeparator()
        if self.interaction is None:
            # menu for item/items
            items = self._itemsAt(spos)
            if items:
                # preference: top grip, selection set, top item
                grips = [item for item in items if isinstance(item, GripItem)]
                if grips:
                    items = [grips[0]] # top grip
                elif any(item.isSelected() for item in items):
                    items = self.scene().selectedItems()  # selection set
                else:
                    items = [items[0]] # top item
                # narrow down to items that support context menus
                items = [item for item in items if isinstance(item, ItemMenuMixin)]
                if len(items) == 0:
                    return
                if len(items) == 1:
                    # item specific actions/submenus
                    _extendMenu(items[0].ctxMenuItems(self))
                else:
                    # multiple items
                    pass
                # get top items (items with no parent)
                top_items = [item for item in items if item.parentItem() is None]
                f = f" ({len(top_items)}/{len(items)})" \
                    if len(top_items) != len(items) else ""
                if top_items:
                    # common actions: slide/move/rotate
                    menu.addAction(f"Slide{f}", lambda: self.ui.editSlide(items, spos))
                    menu.addAction(f"Move{f}", lambda: self.ui.editMove(items, spos))
                    rpos = None if len(top_items) == 1 else spos
                    menu.addAction(
                        "Rotate CW", lambda: self.ui.editRotateCW(items, rpos)
                    )
                    menu.addAction(
                        "Rotate CCW", lambda: self.ui.editRotateCCW(items, rpos)
                    )
                    menu.addSeparator()
                    # common actions: clipboard/delete/duplicate
                    paste_items, _ = paste()
                    menu.addAction(f"Cut{f}", lambda: self.ui.editCut())
                    menu.addAction(f"Copy{f}", lambda: self.ui.editCopy())
                    if paste_items:
                        menu.addAction(f"Paste{f}", lambda: self.ui.editPaste())
                    menu.addAction(f"Delete{f}", lambda: self.ui.editDelete())
                    menu.addAction(f"Duplicate{f}", lambda: self.ui.editDuplicate())
                    menu.addSeparator()
        else:
            # menu for interaction
            _extendMenu(self.interaction.ctxMenuItems(spos))
        # scene properties
        menu.addAction(
            f"{self.__class__.__name__.replace('View', '')} Properties...",
            lambda: self.ui.editDrawingProperties()
        )
        menu.addSeparator()
        # grid
        grid_show_action = menu.addAction(
            "Grid Display", lambda: self.ui.viewGridDisplay(not self.grid.display)
        )
        grid_show_action.setCheckable(True)
        grid_show_action.setChecked(self.grid.display)
        menu.addAction(grid_show_action)
        grid_snap_action = menu.addAction(
            "Grid Snap", lambda: self.ui.viewGridSnap(not self.grid.snap)
        )
        grid_snap_action.setCheckable(True)
        grid_snap_action.setChecked(self.grid.snap)
        menu.addAction(grid_snap_action)
        grid_pitch_menu = Menu("Grid Pitch")
        grid_pitch_menu.addAction("(10,10)", lambda: self.ui.viewGridPitch(10,10))
        grid_pitch_menu.addAction("(5,5)", lambda: self.ui.viewGridPitch(5,5))
        grid_pitch_menu.addAction("(1,1)", lambda: self.ui.viewGridPitch(1,1))
        menu.addMenu(grid_pitch_menu)
        # display menu
        menu.exec(event.globalPos())

    def action(
        self     : "DrawingView",
        text     : str,
        slot     : Callable,
        checked  : bool               | None = None,
        shortcut : QKeySequence | str | None = None,
        icon     : QIcon              | None = None,
        enabled  : bool                      = True
    ):
        action = QAction(text, self)
        action.triggered.connect(slot)
        if checked is not None:
            action.setCheckable(True)
            action.setChecked(checked)
        if shortcut is not None:
            action.setShortcut(shortcut)
        if icon is not None:
            action.setIcon(icon)
        action.setEnabled(enabled)
        return action

    def separator(self : "DrawingView") -> QAction:
        action = QAction(self)
        action.setSeparator(True)
        return action
