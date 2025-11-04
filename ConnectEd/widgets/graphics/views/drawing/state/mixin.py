from typing import Self

from PyQt6.QtCore import QPoint, QPointF

from .base import qkm, DrawingViewStateBase


class ClickMixin(DrawingViewStateBase):
    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        if self.view.interaction is not None:
            if self.view.interaction.commit(self._snap(s)):
                self.view.state.go(self.view.stateIdle)

    def mouseLeftDoubleClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        if self.view.interaction is not None:
            self.view.interaction.complete(self._snap(s))
            self.view.state.go(self.view.stateIdle)

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        if self.view.interaction is not None:
            self.view.interaction.update(self._snap(s))


class DragMixin(DrawingViewStateBase):
    def mouseLeftDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        if self.view.interaction is not None:
            self.view.interaction.update(self._snap(s))

    def mouseLeftDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        if self.view.interaction is not None:
            if self.view.interaction.commit(self._snap(s)):
                self.view.state.go(self.view.stateIdle)



