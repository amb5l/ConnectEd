from __future__ import annotations

from PyQt6.QtCore import Qt, QPoint

from typing import Self, TypeAlias

from ....app import session

from ....core.doc   import DocBinding
from ....core.types import MenuAction, MenuSeparator, MenuEntry

from ...menu import Menu

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Navigator
    MixinSelf: TypeAlias = Self | Navigator
else:
    MixinSelf = Self


class NavigatorMenuMixin:

    _menu        : Menu
    _group_menus : dict[str, Menu]

    def initMenus(self : MixinSelf) -> None:
        # build viewport menu
        self._menu = Menu(self)
        self._menu.addEntries([
            MenuAction("New...", self.fileNew),
            MenuAction("Open...", self.fileOpen),
            MenuSeparator(),
            MenuAction("Expand All", self.expandAll),
            MenuAction("Collapse All", self.collapseAll),
            MenuAction("Increase Font Size", self.increaseFontSize),
            MenuAction("Decrease Font Size", self.decreaseFontSize),
            MenuSeparator(),
            MenuAction("Reset Font Size", self.resetFontSize),
        ])
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        # group menus
        self._group_menus = {}
        for group_name in self._group_items:
            group_menu = Menu(self)
            group_menu.addEntries(self._groupMenuEntries(group_name))
            self._group_menus[group_name] = group_menu

    def _groupMenuEntries(
        self       : MixinSelf,
        group_name : str,
    ) -> list[MenuEntry]:
        entries : list[MenuEntry] = []
        for doc_type in session().docTypes():
            if doc_type.group != group_name:
                continue
            entries.extend(
                doc_type.cls.navGroupContextMenu(self, doc_type)
            )
        return entries

    def showContextMenu(self : Navigator, pos : QPoint) -> None:
        global_pos = self.viewport().mapToGlobal(pos)
        index = self.indexAt(pos)
        if not index.isValid():
            self._menu.exec(global_pos)
            return
        item = self._model.itemFromIndex(index)
        if item is None:
            self._menu.exec(global_pos)
            return
        binding : DocBinding | None = item.data(Qt.ItemDataRole.UserRole)
        if binding is not None:
            menu = Menu(self)
            menu.addEntries(binding.doc.navContextMenu(binding.subject))
            menu.exec(global_pos)
            return
        group_name = item.text()
        group_menu = self._group_menus.get(group_name)
        if group_menu is not None:
            group_menu.exec(global_pos)
            return
        self._menu.exec(global_pos)
