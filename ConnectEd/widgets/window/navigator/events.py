from __future__ import annotations

from typing import Self, TypeAlias

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QKeyEvent, QMouseEvent

from ..tree_view import TreeView

from .types import NavItem

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Navigator
    MixinSelf: TypeAlias = Self | Navigator
else:
    MixinSelf = Self


class NavigatorEventsMixin:

    def keyPressEvent(self : MixinSelf, event : QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            indexes = self.selectedIndexes()
            if len(indexes) == 1:
                item : NavItem | None = \
                    self._model.itemFromIndex(indexes[0])
                if item is not None:
                    self._openRow(item)
                    event.accept()
                    return
        TreeView.keyPressEvent(self, event)

    def mouseDoubleClickEvent(self : MixinSelf, event : QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            index = self.indexAt(event.pos())
            if index.isValid():
                item : NavItem | None = \
                    self._model.itemFromIndex(index)
                if item is not None:
                    self._openRow(item)
                    event.accept()
                    return
        TreeView.mouseDoubleClickEvent(self, event)
