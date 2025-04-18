from typing import Optional

from PyQt6.QtCore   import QPointF, QSizeF
from PyQt6.QtWidgets import QGraphicsItem

from ....elements import Rectangle, cmdRectangle

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


class DrawingApiPlaceMixin:
    place_wip : Optional[QGraphicsItem] = None
    place_pos : Optional[QPointF]

    def placeRectangle(self : 'DrawingView') -> None:
        self._goState(self.State.PlaceRectangle1)

    def placeRectangleCmd(
        self       : 'DrawingView',
        size_or_p2 : QSizeF | QPointF,
        wip        : bool
    ) -> None:
        # TODO get default anchor and pen/brush/text spec from settings
        self.scene().undo_stack.push(cmdRectangle(
            scene      = self.scene(),
            element    = self.place_wip,
            pos        = self.place_pos,
            size_or_p2 = size_or_p2,
            wip        = wip
        ))
        print("placeRectangleCmd", self.place_wip.pos(), self.place_wip.rect().size())

    def placeRectangleBegin(self : 'DrawingView', pos: QPointF) -> None:
        print("placeRectangleBegin")
        self.place_wip = Rectangle()
        self.place_pos = pos
        self.placeRectangleCmd(QSizeF(1,1), True)
        self._goState(self.State.PlaceRectangle2)

    def placeRectangleContinue(self : 'DrawingView', pos: QPointF) -> None:
        print("placeRectangleContinue")
        self.placeRectangleCmd(pos, True)

    def placeRectangleComplete(self : 'DrawingView', pos: QPointF) -> None:
        print("placeRectangleComplete")
        self.placeRectangleCmd(pos, False)
        self.place_wip = None
        self.place_pos = None
        self._goState(self.State.Idle)
