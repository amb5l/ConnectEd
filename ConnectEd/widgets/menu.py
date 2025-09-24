from typing import Self

from PyQt6.QtWidgets import QMenu

from .private import Action


class Menu(QMenu):
    def subMenusDict(self : Self) -> dict[str, "Menu"]:
        return {a.menu().title().replace("&", "") : a.menu() \
            for a in self.actions() if a.menu() is not None}

    def actionsDict(self : Self) -> dict[str, Action]:
        return {a.text().replace("&", "").replace("...", "") : a \
            for a in self.actions() if a.menu() is None}
