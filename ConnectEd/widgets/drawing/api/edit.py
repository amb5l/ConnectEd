from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Drawing


class DrawingApiEditMixin:
    def editCancel(self : 'Drawing') -> None:
        if self.wip:
            self._removeWIP()
        self.state = self.State.Idle

    def editComplete(self : 'Drawing') -> None:
        match self.state:
            case self.State.PlaceRectangle2:
                self.wip.setPoints(
                    self.prev_pos,
                    self._snap(self.mouse.current.logical)
                )
                self._completeWIP()
                self.state = self.State.Idle

    def editSlide(self : 'Drawing') -> None:
        if self.scene.selectedItems():
            self.state = self.State.EditSlide2
        else:
            self.state = self.State.EditSlide1

    def editMove(self : 'Drawing') -> None:
        if self.scene.selectedItems():
            self.state = self.State.EditMove2
        else:
            self.state = self.State.EditMove1
