"""QMenuBar / QMenu discovery by normalized title and action name."""

from typing import Self

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu, QMenuBar


class MenusMixin:
    def menuTitle(self : Self, menu : QMenu) -> str:
        return menu.title().replace("&", "")

    def actionName(self : Self, action : QAction) -> str:
        return action.text().replace("&", "").replace("...", "")

    def menu(self : Self, menu_bar : QMenuBar, title : str) -> QMenu | None:
        for bar_action in menu_bar.actions():
            sub_menu = bar_action.menu()
            if sub_menu is not None and self.menuTitle(sub_menu) == title:
                return sub_menu
        return None

    def action(self : Self, menu : QMenu, name : str) -> QAction | None:
        for menu_action in menu.actions():
            if menu_action.menu() is None and self.actionName(menu_action) == name:
                return menu_action
        return None
