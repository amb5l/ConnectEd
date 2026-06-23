from typing          import Self, overload

from PyQt6.QtWidgets import QMenu, QWidget
from PyQt6.QtGui     import QAction

from ..core.check import checked
from ..core.types import MenuAction, MenuSub, MenuSeparator, MenuEntry

from .action import Action

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .window.sub_window import DocSubWindow


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
    def __init__(
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

    def getSubMenus(self : Self) -> dict[str, "Menu"]:
        return {a.menu().title().replace("&", "") : a.menu() \
            for a in self.actions() if a.menu() is not None}

    def getActions(self : Self) -> dict[str, Action]:
        return {a.text().replace("&", "").replace("...", "") : a \
            for a in self.actions() if a.menu() is None}

    def getAction(self : Self, name : str) -> Action | None:
        actions = self.getActions()
        return actions[name] if name in actions else None


class PlaceMenu(Menu):
    subwindow_class : type["DocSubWindow"] | None = None
