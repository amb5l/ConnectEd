from typing import Self, Callable

from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QContextMenuEvent, QAction

from .....core.xml import paste

from ....menu import Menu

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...items.mixin.menu import ElementMenuMixin
    from . import DrawingView


class DrawingViewMenuMixin:
    def contextMenuEvent(self : "DrawingView", event : QContextMenuEvent) -> None:
        print("contextMenuEvent")
        from ...views.diagram import DiagramView
        vpos = event.pos()
        spos = self.mapToScene(vpos)
        menu = Menu()
        # interaction related actions/submenus (if applicable)
        if self.interaction is not None:
            spos = self.mapToScene(event.pos())
            menu_items = self.interaction.ctxMenuItems(spos)
            if menu_items:
                for menu_item in menu_items:
                    if isinstance(menu_item, QAction):
                        menu.addAction(menu_item)
                    elif isinstance(menu_item, QMenu):
                        menu.addMenu(menu_item)
                menu.addSeparator()
        # get applicable item/items: selection or top item
        items_at = self._itemsAt(spos)
        if any(item.isSelected() for item in items_at):
            items = self.scene().selectedItems()  # selection set
        else:
            for item in items_at:
                if isinstance(item, ElementMenuMixin):
                    items.append(item)  # item at position
            else:
                items = []  # no items at position
        # clipboard/delete/duplicate actions
        paste_items = paste()
        if items or paste_items:
            if items:
                menu.addAction("Cut", self.ui.editCut)
                menu.addAction("Copy", self.ui.editCopy)
            if paste_items:
                menu.addAction("Paste", self.ui.editPaste)
            if items:
                menu.addAction("Delete", self.ui.editDelete)
                menu.addAction("Duplicate", self.ui.editDuplicate)
            menu.addSeparator()


        # EITHER add selection related actions/submenus
        pass
        # OR add element related actions/submenus
        pass
        # query
        menu.addAction("Query", lambda: self.ui.editQuery(spos))
        menu.addSeparator()
        # zoom
        menu.addAction("Zoom All", self.ui.viewZoomAll)
        if isinstance(self, DiagramView):
            menu.addAction("Zoom Sheet", self.ui.viewZoomSheet)
        # grid
        grid_snap_action = menu.addAction(
            "Grid Snap", lambda: self.ui.viewGridSnap(not self.grid.snap)
        )
        grid_snap_action.setCheckable(True)
        grid_snap_action.setChecked(self.grid.snap)
        menu.addAction(grid_snap_action)
        grid_pitch_menu = Menu("Grid Pitch")
        grid_pitch_menu.addAction("10", lambda: self.ui.viewGridPitch(10))
        grid_pitch_menu.addAction("5", lambda: self.ui.viewGridPitch(5))
        grid_pitch_menu.addAction("1", lambda: self.ui.viewGridPitch(1))
        menu.addMenu(grid_pitch_menu)
        # display menu
        menu.exec(event.globalPos())

    def ctxMenuAction(self : Self, text : str, slot : Callable):
        action = QAction(text)
        action.triggered.connect(slot)
        return action

    def ctxMenuSeparator(self : Self) -> QAction:
        action = QAction()
        action.setSeparator(True)
        return action
