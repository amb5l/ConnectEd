from __future__ import annotations

from typing import Self, TypeAlias

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QKeyEvent, QMouseEvent

from PyQt6.QtWidgets import QAbstractItemView

from ....app import logger

from ..tree_view import TreeView

from .types import NavItem


class NavigatorEventsMixin:

    def keyPressEvent(self : Self, event : QKeyEvent | None) -> None:
        from . import Navigator
        if not isinstance(self, Navigator): raise TypeError("Bad host")
        if event is None:
            logger().warning("No event")
            return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.state() == QAbstractItemView.State.EditingState \
                    or self.indexWidget(self.currentIndex()) is not None:
                TreeView.keyPressEvent(self, event)
                return
            indexes = self.selectedIndexes()
            if len(indexes) == 1:
                item = self._model.itemFromIndex(indexes[0])
                if not isinstance(item, NavItem):
                    raise ValueError("Bad item")
                if item is not None:
                    self._openRow(item)
                    event.accept()
                    return
        TreeView.keyPressEvent(self, event)

    def mouseDoubleClickEvent(self : Self, e : QMouseEvent | None) -> None:
        from . import Navigator
        if not isinstance(self, Navigator): raise TypeError("Bad host")
        if e is None:
            logger().warning("No event")
            return
        if e.button() == Qt.MouseButton.LeftButton:
            index = self.indexAt(e.pos())
            if index.isValid():
                item = self._model.itemFromIndex(index)
                if not isinstance(item, NavItem):
                    raise ValueError("Bad item")
                if item is not None:
                    self._openRow(item)
                    e.accept()
                    return
        TreeView.mouseDoubleClickEvent(self, e)
