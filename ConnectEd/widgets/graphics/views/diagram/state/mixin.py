from __future__ import annotations

from typing          import Self, TYPE_CHECKING
from collections.abc import Callable

from PyQt6.QtCore    import QPoint, QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ..mouse import MouseModifier

if TYPE_CHECKING:
    from ..            import DiagramView
    from ..interaction import DiagramInteraction
    from .base         import DiagramViewState


class StartMixin:
    """
    For states that need a click (or context-menu Start) to create an
    interaction and advance to the next state.
    """

    # Constructors take (view, first snap point); item is created inside.
    _INTERACTION_CLS : Callable[[DiagramView, QPointF], DiagramInteraction]

    def _nextState(self : Self) -> DiagramViewState:
        raise NotImplementedError

    def _start(self : Self, spos : QPointF) -> None:
        from .base import DiagramViewState
        if not isinstance(self, DiagramViewState): raise TypeError("Bad host")
        self.interact(
            self._INTERACTION_CLS(self.view, spos),
            self._nextState()
        )

    def ctxMenuItems(self : Self, spos : QPointF) -> list[QAction | QMenu]:
        from .base import DiagramViewState
        if not isinstance(self, DiagramViewState): raise TypeError("Bad host")
        spos = self.view._snap(spos)
        return [
            self.view.action("Start", lambda: self._start(spos)),
            self.view.action("Cancel", lambda: self.view.state.go(self.view.stateIdle)),
        ]


class ClickMixin:
    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        from .base import DiagramViewState
        if not isinstance(self, DiagramViewState): raise TypeError("Bad host")
        if self._commit(spos):
            self.view.state.go(self.view.stateIdle)

    def mouseLeftDoubleClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        from .base import DiagramViewState
        if not isinstance(self, DiagramViewState): raise TypeError("Bad host")
        if self._complete(spos):
            self.view.state.go(self.view.stateIdle)

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        from .base import DiagramViewState
        if not isinstance(self, DiagramViewState): raise TypeError("Bad host")
        self._update(spos)


class DragMixin:
    def mouseLeftDragCont(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier) -> None:
        from .base import DiagramViewState
        if not isinstance(self, DiagramViewState): raise TypeError("Bad host")
        self._update(spos)

    def mouseLeftDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        from .base import DiagramViewState
        if not isinstance(self, DiagramViewState): raise TypeError("Bad host")
        if self._commit(spos):
            self.view.state.go(self.view.stateIdle)
