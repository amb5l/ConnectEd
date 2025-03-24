from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


class DrawingApiPlaceMixin:
    def placeRectangle(self : 'DrawingView') -> None:
        self._goState(self.State.PlaceRectangle1)
