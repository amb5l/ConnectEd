from typing import Self

from PyQt6.QtCore import QPoint, QPointF

from .base import qkm


class ClickMixin:
    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        if self._commit(s):
            self.view.state.go(self.view.stateIdle)

    def mouseLeftDoubleClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        if self._complete(s):
            self.view.state.go(self.view.stateIdle)

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self._update(s)


class DragMixin:
    def mouseLeftDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self._update(s)

    def mouseLeftDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        if self._commit(s):
            self.view.state.go(self.view.stateIdle)
