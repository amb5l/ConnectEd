from typing import Self, TYPE_CHECKING

from PyQt6.QtCore    import QPoint, QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from .base import qkm

if TYPE_CHECKING:
    from ..interaction import DrawingInteraction
    from .base         import DrawingViewStateBase


class StartMixin:
    """
    For states that need a click (or context-menu Start) to create an
    interaction and advance to the next state.
    """

    _INTERACTION_CLS : type["DrawingInteraction"]

    def _nextState(self : Self) -> "DrawingViewStateBase":
        raise NotImplementedError

    def _start(self : Self, spos : QPointF) -> None:
        self.interact(
            self._INTERACTION_CLS(self.view, spos),
            self._nextState()
        )

    def ctxMenuItems(self : Self, spos : QPointF) -> list[QAction | QMenu]:
        spos = self._snap(spos)
        return [
            self.view.action("Start", lambda: self._start(spos)),
            self.view.action("Cancel", lambda: self.view.state.go(self.view.stateIdle)),
        ]


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
