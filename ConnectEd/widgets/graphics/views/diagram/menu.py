from __future__ import annotations

from typing          import Self

from collections.abc import Callable

from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QContextMenuEvent, QAction, QKeySequence, QIcon

from .....app import logger

from .....core.xml import clipboardHasData

from ....menu import Menu

from ...items.grip import GripItem


from .host import asDiagramView


class DiagramViewMenuMixin:

    def contextMenuEvent(self : Self, event : QContextMenuEvent | None) -> None:
        host = asDiagramView(self)
        if event is None:
            logger().warning("No event")
            return
        from ...items.mixin.menu import ItemMenuMixin
        vpos = event.pos()
        spos = host.mapToScene(vpos)
        menu = Menu()
        def _extendMenu(menu_items : list[QAction | QMenu]) -> None:
            if menu_items:
                for menu_item in menu_items:
                    if isinstance(menu_item, QAction):
                        menu.addAction(menu_item)
                    elif isinstance(menu_item, QMenu):
                        menu.addMenu(menu_item)
                menu.addSeparator()
        if host.interaction is not None:
            _extendMenu(host.interaction.ctxMenuItems(spos))
        elif (state_items := host.state.ctxMenuItems(spos)):
            _extendMenu(state_items)
        else:
            # menu for item/items
            items_at = host._itemsAt(vpos)
            if items_at:
                # preference: top grip, selection set, top menu-capable item
                grips = [item for item in items_at if isinstance(item, GripItem)]
                if grips:
                    items = [grips[0]] # top grip
                elif any(item.isSelected() for item in items_at):
                    scene = host.scene()
                    if scene is None:
                        raise TypeError("No scene")
                    items = scene.selectedItems()  # selection set
                else:
                    menu_capable = [
                        item for item in items_at if isinstance(item, ItemMenuMixin)
                    ]
                    items = [menu_capable[0]] if menu_capable else [items_at[0]]
                # narrow down to items that support context menus
                items = [item for item in items if isinstance(item, ItemMenuMixin)]
                if len(items) == 0:
                    return
                if len(items) == 1:
                    # item specific actions/submenus
                    _extendMenu(items[0].ctxMenuItems(host, spos))
                else:
                    # multiple items
                    _extendMenu([
                        host.action(
                            "Appearance...", lambda: host.editAppearance(items)
                        ),
                        host.action(
                            "Properties...", lambda: host.editItemProperties(items)
                        ),
                        host.separator()
                    ])
                # get top items (items with no parent)
                top_items = [item for item in items if item.parentItem() is None]
                f = f" ({len(top_items)}/{len(items)})" \
                    if len(top_items) != len(items) else ""
                if top_items:
                    # common actions: slide/move/rotate
                    menu.addAction(f"Slide{f}", lambda: host.editSlide(top_items, spos))
                    menu.addAction(f"Move{f}", lambda: host.editMove(top_items, spos))
                    rpos = None if len(top_items) == 1 else spos
                    menu.addAction(
                        "Rotate CW", lambda: host.editRotateCW(items, rpos)
                    )
                    menu.addAction(
                        "Rotate CCW", lambda: host.editRotateCCW(items, rpos)
                    )
                    menu.addSeparator()
                    # common actions: clipboard/delete/duplicate
                    menu.addAction(f"Cut{f}", lambda: host.editCut())
                    menu.addAction(f"Copy{f}", lambda: host.editCopy())
                    if clipboardHasData():
                        menu.addAction(f"Paste{f}", lambda: host.editPaste())
                    menu.addAction(f"Delete{f}", lambda: host.editDelete())
                    menu.addAction(f"Duplicate{f}", lambda: host.editDuplicate())
                    menu.addSeparator()
        # scene properties
        menu.addAction(
            f"{host.__class__.__name__.replace('View', '')} Properties...",
            lambda: host.editDiagramProperties()
        )
        menu.addSeparator()
        # grid
        grid_show_action = menu.addAction(
            "Grid Display", lambda: host.viewGridDisplay(not host.grid.display)
        )
        if grid_show_action is None:
            raise RuntimeError("No grid show action")
        grid_show_action.setCheckable(True)
        grid_show_action.setChecked(host.grid.display)
        menu.addAction(grid_show_action)
        grid_snap_action = menu.addAction(
            "Grid Snap", lambda: host.viewGridSnap(not host.grid.snap)
        )
        if grid_snap_action is None:
            raise RuntimeError("No grid snap action")
        grid_snap_action.setCheckable(True)
        grid_snap_action.setChecked(host.grid.snap)
        menu.addAction(grid_snap_action)
        grid_pitch_menu = Menu("Grid Pitch")
        grid_pitch_menu.addAction("(10,10)", lambda: host.viewGridPitch(10,10))
        grid_pitch_menu.addAction("(5,5)", lambda: host.viewGridPitch(5,5))
        grid_pitch_menu.addAction("(1,1)", lambda: host.viewGridPitch(1,1))
        menu.addMenu(grid_pitch_menu)
        # display menu
        menu.exec(event.globalPos())

    def action(
        self     : Self,
        text     : str,
        slot     : Callable,
        checked  : bool               | None = None,
        shortcut : QKeySequence | str | None = None,
        icon     : QIcon              | None = None,
        enabled  : bool                      = True
    ):
        host = asDiagramView(self)
        action = QAction(text, host)
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

    def separator(self : Self) -> QAction:
        host = asDiagramView(self)
        action = QAction(host)
        action.setSeparator(True)
        return action
