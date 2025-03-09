from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Drawing


class DrawingApiEditMixin:
    def editCancel(self : 'Drawing') -> None:
        if self.wip:
            self._removeWIP()
        self.state = self.State.Idle
