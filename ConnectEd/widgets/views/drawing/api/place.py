from typing import Self, Optional

from PyQt6.QtCore   import QPointF, QSizeF
from PyQt6.QtWidgets import QGraphicsItem

from ....elements import Rectangle, cmdPlaceRectangle


class DrawingApiPlaceMixin:
    place_wip : Optional[QGraphicsItem] = None
    place_pos : Optional[QPointF]

    def placeRectangle(self : Self) -> None:
        self._goState(self.State.PlaceRectangle1)

    def placeRectangleCmd(
        self       : Self,
        size_or_p2 : QSizeF | QPointF,
        wip        : bool
    ) -> None:
        # TODO get default anchor and pen/brush/text spec from settings
        self.scene().undo_stack.push(cmdPlaceRectangle(
            scene      = self.scene(),
            element    = self.place_wip,
            pos        = self.place_pos,
            size_or_p2 = size_or_p2,
            wip        = wip
        ))

    def placeRectangleBegin(self : Self, pos: QPointF) -> None:
        self.place_wip = Rectangle()
        self.place_pos = pos
        self.placeRectangleCmd(QSizeF(1,1), True)
        self._goState(self.State.PlaceRectangle2)

    def placeRectangleContinue(self : Self, pos: QPointF) -> None:
        self.placeRectangleCmd(pos, True)

    def placeRectangleComplete(self : Self, pos: QPointF) -> None:
        self.placeRectangleCmd(pos, False)
        self.place_wip = None
        self.place_pos = None
        self._goState(self.State.Idle)
