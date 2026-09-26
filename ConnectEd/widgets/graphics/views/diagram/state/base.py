from __future__ import annotations

from typing          import Self
from collections.abc import Sequence

from PyQt6.QtCore    import Qt, QPoint, QPointF
from PyQt6.QtWidgets import QGraphicsItem, QMenu
from PyQt6.QtGui     import QAction

from ......app        import window

from ......core.check import checked

from ..interaction    import DiagramInteraction
from ..mouse          import MouseModifier

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.diagram import DiagramScene
    from ..                 import DiagramView


qkm = Qt.KeyboardModifier


class DiagramViewState:
    """Base class for all diagram view states."""

    # class attributes
    STATUS : str

    # instance attributes
    view   : DiagramView
    scene  : DiagramScene

    @checked
    def __init__(self : Self, view : DiagramView) -> None:
        self.view = view
        if (scene := view.scene()) is None:
            raise TypeError("Bad scene")
        self.scene = scene

    @checked
    def entry(
        self  : Self,
        items : Sequence[QGraphicsItem],
        spos  : QPointF
    ) -> None:
        """Override when the state needs setup beyond go()'s interaction install."""
        pass

    @checked
    def go(
        self        : Self,
        state       : DiagramViewState,
        items       : QGraphicsItem | Sequence[QGraphicsItem] | None = None,
        interaction : DiagramInteraction                      | None = None
    ) -> None:
        if items is None:
            items = []
        elif isinstance(items, QGraphicsItem):
            items = [items]
        self._setInteraction(interaction)
        self.view.state = state
        status = state.STATUS
        if items is not None and len(items) == 1:
            status = status.replace("{Item}", items[0].__class__.__name__)
        else:
            status = status.replace("{Item}", "Item")
        status.replace(
            "{Diagram}", self.scene.__class__.__name__.replace("Scene", "")
        )
        window().statusBar().status.setText(state.STATUS)
        state.entry(items, self.view._mouse_spos)

    @checked
    def interact(
        self        : Self,
        interaction : DiagramInteraction,
        state       : DiagramViewState | None = None
    ) -> None:
        if not interaction.valid():
            self.view.state.go(self.view.stateIdle)
            return
        if state is not None:
            self.go(state, interaction=interaction)
        else:
            # No state transition; just swap the interaction in place.
            self._setInteraction(interaction)

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        pass

    def mouseLeftDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        pass

    def mouseLeftDragCont(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        pass

    def mouseLeftDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        pass

    def mouseLeftDoubleClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        pass

    def mouseMiddleClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        pass

    def mouseMiddleDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        pass

    def mouseMiddleDragCont(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        pass

    def mouseMiddleDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        pass

    def mouseMiddleDoubleClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        pass

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : MouseModifier
    ) -> None:
        pass

    def ctxMenuItems(self : Self, spos : QPointF) -> list[QAction | QMenu]:
        return []

    @checked
    def _setInteraction(
        self        : Self,
        interaction : DiagramInteraction | None
    ) -> None:
        """Install ``interaction`` as the view's live interaction, cancelling
        the previous one if there was a different one. ``cancel()`` is a no-op
        on already-done interactions (see ``Interaction``), so this is safe to
        call after a successful ``commit``/``complete`` too.
        """
        old = self.view.interaction
        if old is not None and old is not interaction:
            old.cancel()
        self.view.interaction = interaction

    def _interaction(self : Self) -> DiagramInteraction:
        if (interaction := self.view.interaction) is None:
            raise RuntimeError("No interaction")
        return interaction

    def _update(self : Self, s : QPointF) -> None:
        if isinstance(self.view.interaction, DiagramInteraction):
            self.view.interaction.update(self.view._snap(s))

    def _commit(self : Self, s : QPointF) -> bool:
        if isinstance(self.view.interaction, DiagramInteraction):
            return self.view.interaction.commit(self.view._snap(s))
        return False

    def _complete(self : Self, s : QPointF) -> bool:
        if isinstance(self.view.interaction, DiagramInteraction):
            self.view.interaction.complete(self.view._snap(s))
            return True
        return False
