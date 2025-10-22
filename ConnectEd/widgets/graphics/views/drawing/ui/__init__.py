from typing import Self

from .edit  import DrawingViewUiEditMixin
from .view  import DrawingViewUiViewMixin
from .place import DrawingViewUiPlaceMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


class DrawingViewUi(
    DrawingViewUiEditMixin,
    DrawingViewUiViewMixin,
    DrawingViewUiPlaceMixin
):
    _view : "DrawingView"

    def __init__(self : Self, view : "DrawingView") -> None:
        self._view = view
