from typing import Self

from PyQt6.QtCore import Qt, QPoint, QPointF

from ......app import window

from ....items import ItemMixin

from ....scenes.drawing import DrawingScene

from ..interaction import Interaction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


qkm = Qt.KeyboardModifier


class DrawingViewStateBase:
    # instance attributes
    view   : "DrawingView"
    scene  : "DrawingScene"

    def __init__(self : Self, view : "DrawingView") -> None:
        self.view = view
        self.scene = view.scene()

    def go(
        self  : Self,
        state : "DrawingViewStateBase",
        items : list[ItemMixin] | None = None
    ) -> None:
        if state == self.view.stateIdle:
            self.view.interaction = None
        self.view.state = state
        if window() is not None:
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
        if interaction.valid:
            self.view.interaction = interaction
            if state is not None:
                self.go(state)
        else:
            self.view.state.go(self.view.stateIdle)

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
