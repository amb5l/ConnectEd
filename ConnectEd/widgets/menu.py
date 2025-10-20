from typing import Self

from PyQt6.QtWidgets import QMenu

from .private import Action

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .window.sub_window import SubWindow


class Menu(QMenu):
    def subMenusDict(self : Self) -> dict[str, "Menu"]:
        return {a.menu().title().replace("&", "") : a.menu() \
            for a in self.actions() if a.menu() is not None}

    def actionsDict(self : Self) -> dict[str, Action]:
        return {a.text().replace("&", "").replace("...", "") : a \
            for a in self.actions() if a.menu() is None}


class PlaceMenu(Menu):
    subwindow_class : type["SubWindow"] | None = None
