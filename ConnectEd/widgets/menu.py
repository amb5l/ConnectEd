from __future__ import annotations

from typing import Self, overload

from PyQt6.QtWidgets import QMenu, QWidget
from PyQt6.QtGui     import QAction

from ..core.check import checked
from ..core.types import MenuAction, MenuSub, MenuSeparator, MenuEntry

from .action import Action


class Menu(QMenu):

    @overload
    def __init__(
        self   : Self,
        parent : QWidget | None = None
    ) -> None:
        ...

    @overload
    def __init__(
        self   : Self,
        title  : str | None = None,
        parent : QWidget | None = None
    ) -> None:
        ...

    @checked
    def __init__(  # pyright: ignore[reportInconsistentOverload]
        self            : Self,
        title_or_parent : str | QWidget | None = None,
        parent_or_none  : QWidget | None = None
    ) -> None:
        if isinstance(title_or_parent, str):
            title = title_or_parent
            parent = parent_or_none
        else:
            title = None
            parent = title_or_parent
        super().__init__(title, parent)

    def addEntries(self : Self, entries : list[MenuEntry]) -> None:
        for entry in entries:
            if isinstance(entry, MenuSub):
                menu = Menu(entry.label)
                menu.addEntries(entry.items)
                self.addMenu(menu)
            elif isinstance(entry, MenuAction):
                action = QAction(entry.label, self)
                action.setEnabled(entry.enabled)
                handler = entry.handler
                action.triggered.connect(
                    lambda _checked=False, handler=handler: handler()
                )
                self.addAction(action)
            elif isinstance(entry, MenuSeparator):
                self.addSeparator()

    def getSubMenus(self : Self) -> dict[str, Menu]:
        submenus = {}
        for a in self.actions():
            if (menu := a.menu()) is None:
                raise RuntimeError("No menu")
            submenus[menu.title().replace("&", "")] = a.menu()
        return submenus

    def getActions(self : Self) -> dict[str, Action]:
        actions = {}
        for a in self.actions():
            if not isinstance(a, Action):
                raise RuntimeError("Bad action")
            actions[a.text().replace("&", "").replace("...", "")] = a
        return actions

    def getAction(self : Self, name : str) -> Action | None:
        actions = self.getActions()
        return actions[name] if name in actions else None


class PlaceMenu(Menu):
    subwindow_cls : type | None = None
