from typing import Self

from PyQt6.QtCore import Qt, QPoint, QPointF

from ......app import window

from ....items.mixin import ItemMixin

from ....scenes.drawing import DrawingScene

from ..interaction import Interaction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


qkm = Qt.KeyboardModifier


class DrawingViewStateBase:
    # class attributes
    STATUS : str

    # instance attributes
    view   : "DrawingView"
    scene  : "DrawingScene"

    def __init__(self : Self, view : "DrawingView") -> None:
        self.view = view
        self.scene = view.scene()

    def go(
        self        : Self,
        state       : "DrawingViewStateBase",
        items       : list[ItemMixin] | None = None,
        interaction : Interaction | None = None
    ) -> None:
        self._setInteraction(interaction)
        self.view.state = state
        if window() is not None:
            status = state.STATUS
            if items is not None and len(items) == 1:
                status = status.replace("{Item}", items[0].__class__.__name__)
            else:
                status = status.replace("{Item}", "Item")
            status.replace(
                "{Drawing}", self.scene.__class__.__name__.replace("Scene", "")
            )
            window().status_bar.status.setText(state.STATUS)
        state.entry(
            self.view.mouse.current.physical,
            self.view.mouse.current.logical,
            items
        )

    def interact(
        self        : Self,
        interaction : Interaction,
        state       : "DrawingViewStateBase | None" = None
    ) -> None:
        if not interaction.valid():
            self.view.state.go(self.view.stateIdle)
            return
        if state is not None:
            self.go(state, interaction=interaction)
        else:
            # No state transition; just swap the interaction in place.
            self._setInteraction(interaction)

    def _setInteraction(
        self        : Self,
        interaction : Interaction | None
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

    def entry(
        self : Self,
        v    : QPoint,
        s    : QPointF,
        i    : list[ItemMixin] | None = None
    ) -> None:
        pass

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseLeftDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseLeftDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseLeftDoubleClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseMiddleClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseMiddleDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseMiddleDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseMiddleDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def _snap(self : Self, s : QPointF) -> QPointF:
        return self.view._snap(s)

    def _update(self : Self, s : QPointF) -> None:
        if self.view.interaction is not None:
            self.view.interaction.update(self._snap(s))

    def _commit(self : Self, s : QPointF) -> bool:
        if self.view.interaction is not None:
            return self.view.interaction.commit(self._snap(s))
        return False

    def _complete(self : Self, s : QPointF) -> bool:
        if self.view.interaction is not None:
            self.view.interaction.complete(self._snap(s))
            return True
        return False
