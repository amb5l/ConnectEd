from typing import Self, TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


class DrawingApiEditMixin:
    def editUndo(self : Self) -> None:
        self.scene().undo_stack.undo()

    def editRedo(self : Self) -> None:
        self.scene().undo_stack.redo()

    def editCancel(self : Self) -> None:
        if self.wip:
            self._removeWIP()
        self._goState(self.State.Idle)

    def editComplete(self : Self) -> None:
        match self.state:
            case self.State.PlaceRectangle2:
                self.wip.setPoints(
                    self.prev_pos,
                    self._snap(self.mouse.current.logical)
                )
                self._completeWIP()
                self._goState(self.State.Idle)

    def editSlide(self : Self) -> None:
        if self.scene().selectedItems():
            self._goState(self.State.EditSlide2)
        else:
            self._goState(self.State.EditSlide1)

    def editMove(self : Self) -> None:
        if self.scene().selectedItems():
            self._goState(self.State.EditMove2)
        else:
            self._goState(self.State.EditMove1)
