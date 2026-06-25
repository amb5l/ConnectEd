from __future__ import annotations

from typing          import Self, TypeAlias
from collections.abc import Callable

from PyQt6.QtCore import Qt

from ....app import logger, session

from ....core.doc import NavItemSpec, Doc, DocBinding

from .types import NavItem, NavDummyItem, NavModel

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..sub_window import DocSubWindow
    from . import Navigator
    MixinSelf: TypeAlias = Self | Navigator
else:
    MixinSelf = Self

class NavigatorPrivateMixin:

    def _forEachNavItem(
        self : MixinSelf,
        fn   : Callable[[NavItem], None],
    ) -> None:
        for row in range(self._model.rowCount()):
            item = self._model.item(row)
            if item is not None:
                self._forEachNavItemFrom(item, fn)

    def _forEachNavItemFrom(
        self : MixinSelf,
        item : NavItem,
        fn   : Callable[[NavItem], None],
    ) -> None:
        fn(item)
        for row in range(item.rowCount()):
            child = item.child(row)
            if child is not None:
                self._forEachNavItemFrom(child, fn)

    def _refreshDocNav(self : MixinSelf, doc : Doc) -> None:
        def refresh(item : NavItem) -> None:
            binding : DocBinding | None = \
                item.data(Qt.ItemDataRole.UserRole)
            if binding is None or binding.doc is not doc:
                return
            if isinstance(binding.subject, str):
                return
            display_label = doc.navDisplayLabel(binding.subject)
            if item.text() != display_label:
                item.setText(display_label)
            tip = doc.navToolTip(binding.subject)
            if tip is not None and item.toolTip() != tip:
                item.setToolTip(tip)
        self._forEachNavItem(refresh)

    def _docNavItem(self : MixinSelf, doc : Doc) -> NavItem | None:
        for group_item in self._group_items.values():
            for row in range(group_item.rowCount()):
                child = group_item.child(row)
                if isinstance(child, NavDummyItem):
                    continue
                binding : DocBinding | None = \
                    child.data(Qt.ItemDataRole.UserRole)
                if binding is not None and binding.doc is doc:
                    return child
        return None

    def _removeDocFromTree(self : MixinSelf, doc : Doc) -> None:
        doc_item = self._docNavItem(doc)
        if doc_item is None:
            return
        parent = doc_item.parent()
        if parent is None:
            return
        parent.removeRow(doc_item.row())
        self._updateGroups()

    def _closeSubwindowsForDoc(self : MixinSelf, doc : Doc) -> None:
        from ....app import window
        from ..sub_window import DocSubWindow
        mdi_area = window().mdiArea()
        for subwindow in list(mdi_area.subWindowList()):
            if not isinstance(subwindow, DocSubWindow):
                continue
            binding = subwindow.docBinding()
            if binding is None or binding.doc is not doc:
                continue
            subwindow.close()

    def _subwindowsForDoc(
        self    : MixinSelf,
        doc     : Doc,
        exclude : DocSubWindow | None = None,
    ) -> list[DocSubWindow]:
        from ....app import window
        from ..sub_window import DocSubWindow
        subwindows = []
        for subwindow in window().mdiArea().subWindowList():
            if not isinstance(subwindow, DocSubWindow):
                continue
            if subwindow is exclude:
                continue
            binding = subwindow.docBinding()
            if binding is not None and binding.doc is doc:
                subwindows.append(subwindow)
        return subwindows

    def _initGroups(self : MixinSelf) -> None:
        for doc_type in session().docTypes():
            # row item
            group_name = doc_type.group
            group_item = NavItem(group_name)
            group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            font = group_item.font()
            font.setBold(True)
            group_item.setFont(font)
            self._model.appendRow(group_item)
            self._group_items[group_name] = group_item

    def _updateGroups(self : MixinSelf) -> None:
        for group_item in self._group_items.values():
            if group_item.rowCount() == 0:
                group_item.appendRow(NavDummyItem("<none loaded>"))
            elif group_item.rowCount() == 1:
                pass
            else:
                for row in range(group_item.rowCount()):
                    child_item = group_item.child(row)
                    if isinstance(child_item, NavDummyItem):
                        group_item.removeRow(row)
                        break

    def _addDoc(
        self   : MixinSelf,
        parent : NavItem | NavModel,
        doc    : Doc,
        path   : str = ""
    ) -> None:
        def _addRows(
            parent : NavItem | NavModel,
            specs  : NavItemSpec | list[NavItemSpec],
        ) -> NavItem | None:
            if not isinstance(specs, list):
                specs = [specs]
            root_item : NavItem | None = None
            for spec in specs:
                label = spec.subject if isinstance(spec.subject, str) \
                    else doc.navDisplayLabel(spec.subject)
                item = NavItem(label)
                if isinstance(spec.subject, str):
                    # static string (typically a container)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    if spec.tip is not None:
                        item.setToolTip(spec.tip)
                else:
                    tip = doc.navToolTip(spec.subject)
                    if tip is None and spec.tip is not None:
                        tip = spec.tip
                    if tip is not None:
                        item.setToolTip(tip)
                item.setData(
                    DocBinding(doc, spec.subject),
                    Qt.ItemDataRole.UserRole,
                )
                parent.appendRow(item)
                if root_item is None:
                    root_item = item
                if spec.children is not None:
                    _addRows(item, spec.children)
            return root_item
        doc_item = _addRows(parent, doc.navItemSpec())
        if doc_item is not None:
            self._openRow(doc_item)
        self._updateGroups()

    def _openRow(self : MixinSelf, item : NavItem) -> bool:
        binding : DocBinding | None = \
            item.data(Qt.ItemDataRole.UserRole)
        if binding is not None:
            if binding.subject is not None:
                ok = binding.doc.showWindow(binding.subject)
            else:
                ok = binding.doc.openDefault()
            if not ok:
                name = item.text()
                logger().warning(
                    f"Failed to open {name!r} "
                    f"({type(binding.doc).__name__})"
                )
            return ok
        index = self._model.indexFromItem(item)
        if index.isValid() and self._model.rowCount(index) > 0:
            self.setExpanded(index, not self.isExpanded(index))
        return True
