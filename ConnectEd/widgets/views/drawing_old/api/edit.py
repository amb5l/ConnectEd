from typing import Self


class DrawingApiEditMixin:
    def editUndo(self : Self) -> None:
        self.scene().undo_stack.undo()

    def editRedo(self : Self) -> None:
        self.scene().undo_stack.redo()

    def editCancel(self : Self) -> None:
        # TODO: pop command
        self._goState(self.State.Idle)

    def editComplete(self : Self) -> None:
        match self.state:
            case self.State.PlaceRectangle2:
                self.placeRectangleComplete(
                    self._snap(self.mouse.current.logical)
                )

    def editCut(self : Self) -> None:
        print('TODO: editCut')

    def editCopy(self : Self) -> None:
        print('TODO: editCopy')

    def editPaste(self : Self) -> None:
        print('TODO: editPaste')

    def editDelete(self : Self) -> None:
        print('TODO: editDelete')

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
