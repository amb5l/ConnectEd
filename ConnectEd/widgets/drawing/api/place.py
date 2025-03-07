from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Drawing


class DrawingApiPlaceMixin:
    def placeRectangle(self : 'Drawing') -> None:
        self.state = self.State.PlaceRectangle1
