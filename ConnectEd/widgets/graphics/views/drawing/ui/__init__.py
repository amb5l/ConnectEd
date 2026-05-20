from typing import Self

from PyQt6.QtCore import QPointF

from ......core.check import checked

from .edit  import DrawingViewUiEditMixin
from .view  import DrawingViewUiViewMixin
from .place import DrawingViewUiPlaceMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.drawing import DrawingScene
    from .. import DrawingView


class DrawingViewUi(
    DrawingViewUiEditMixin,
    DrawingViewUiViewMixin,
    DrawingViewUiPlaceMixin
):
    _view  : "DrawingView"
    _scene : "DrawingScene"

    @checked
    def __init__(self : Self, view : "DrawingView") -> None:
        self._view = view
        self._scene = view.scene()

    @checked
    def _snap(self : Self, pos : QPointF | None) -> QPointF:
        return self._view._snap(pos)
