from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


class DrawingApiEditMixin:
    def editUndo(self : 'DrawingView') -> None:
        self.scene().undo_stack.undo()

    def editRedo(self : 'DrawingView') -> None:
        self.scene().undo_stack.redo()

    def editCancel(self : 'DrawingView') -> None:
        if self.wip:
            self._removeWIP()
        self._goState(self.State.Idle)

    def editComplete(self : 'DrawingView') -> None:
        match self.state:
            case self.State.PlaceRectangle2:
                self.wip.setPoints(
                    self.prev_pos,
                    self._snap(self.mouse.current.logical)
                )
                self._completeWIP()
                self._goState(self.State.Idle)

    def editSlide(self : 'DrawingView') -> None:
        if self.scene().selectedItems():
            self._goState(self.State.EditSlide2)
        else:
            self._goState(self.State.EditSlide1)

    def editMove(self : 'DrawingView') -> None:
        if self.scene().selectedItems():
            self._goState(self.State.EditMove2)
        else:
            self._goState(self.State.EditMove1)
