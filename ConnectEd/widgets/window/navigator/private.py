from __future__ import annotations

from typing import Self, TypeAlias

from PyQt6.QtCore import Qt

from ....app import logger

from ....core.doc import NavItemSpec, Doc, DocBinding

from .types import NavItem, NavModel

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Navigator
    MixinSelf: TypeAlias = Self | Navigator
else:
    MixinSelf = Self

class NavigatorPrivateMixin:

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
                text = spec.subject if isinstance(spec.subject, str) \
                    else spec.subject.name()
                item = NavItem(text)
                if isinstance(spec.subject, str):
                    # static string (typically a container)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    item.setData(
                        DocBinding(doc, spec.subject),
                        Qt.ItemDataRole.UserRole,
                    )
                if spec.tip is not None:
                    item.setToolTip(spec.tip)
                parent.appendRow(item)
                if root_item is None:
                    root_item = item
                if spec.children is not None:
                    _addRows(item, spec.children)
            return root_item
        doc_item = _addRows(parent, doc.navItemSpec())
        if doc_item is not None:
            self._openRow(doc_item)

    def _openRow(self : MixinSelf, item : NavItem) -> bool:
        binding : DocBinding | None = \
            item.data(Qt.ItemDataRole.UserRole)
        if binding is not None:
            if binding.subject is not None:
                ok = binding.doc.openWindow(binding.subject)
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
