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
                self.wip.setPoint2(
                    self._snap(self.mouse.current.logical)
                )
                self._completeWIP()
                self.state = self.State.Idle
