from typing import Self

from PyQt6.QtCore import QPointF

from ...drawing.ui import DrawingViewUi

from .place import DiagramViewUiPlaceMixin


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.diagram import DiagramScene
    from .. import DiagramView


class DiagramViewUi(
    DiagramViewUiPlaceMixin,
    DrawingViewUi
):
    _view  : "DiagramView"
    _scene : "DiagramScene"
