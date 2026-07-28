from __future__ import annotations

from typing          import Self, TYPE_CHECKING
from collections.abc import Callable

from PyQt6.QtCore    import QPoint, QPointF
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui     import QAction

from ..mouse import MouseModifier

from .host import asDiagramViewState
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
        host = asDiagramViewState(self)
        host.interact(
            self._INTERACTION_CLS(host.view, spos),
            self._nextState()
        )

    def ctxMenuItems(self : Self, spos : QPointF) -> list[QAction | QMenu]:
        host = asDiagramViewState(self)
        spos = host.view._snap(spos)
        return [
            host.view.action("Start", lambda: self._start(spos)),
            host.view.action("Cancel", lambda: host.view.state.go(host.view.stateIdle)),
        ]


class ClickMixin:
    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        host = asDiagramViewState(self)
        if host._commit(spos):
            host.view.state.go(host.view.stateIdle)

    def mouseLeftDoubleClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        host = asDiagramViewState(self)
        if host._complete(spos):
            host.view.state.go(host.view.stateIdle)

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        host = asDiagramViewState(self)
        host._update(spos)


class DragMixin:
    def mouseLeftDragCont(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier) -> None:
        host = asDiagramViewState(self)
        host._update(spos)

    def mouseLeftDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        host = asDiagramViewState(self)
        if host._commit(spos):
            host.view.state.go(host.view.stateIdle)
