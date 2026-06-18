from __future__ import annotations

from typing import Self, TypeAlias

from PyQt6.QtCore import Qt

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
            parent : NavItem,
            specs  : NavItemSpec | list[NavItemSpec]
        ) -> None:
            if not isinstance(specs, list):
                specs = [specs]
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
                if spec.children is not None:
                    _addRows(item, spec.children)
        _addRows(self._model, doc.navItemSpec())

    def _openRow(self : MixinSelf, item : NavItem) -> None:
        binding : DocBinding | None = \
            item.data(Qt.ItemDataRole.UserRole)
        if binding is not None:
            if binding.subject is not None:
                binding.doc.openWindow(binding.subject)
            else:
                binding.doc.openDefault()
            return
        index = self._model.indexFromItem(item)
        if index.isValid() and self._model.rowCount(index) > 0:
            self.setExpanded(index, not self.isExpanded(index))
