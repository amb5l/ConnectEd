from ...drawing.ui import DrawingViewUi

from .place import DiagramViewUiPlaceMixin
from .test  import DiagramViewUiTestMixin


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....scenes.diagram import DiagramScene
    from .. import DiagramView


class DiagramViewUi(
    DiagramViewUiPlaceMixin,
    DiagramViewUiTestMixin,
    DrawingViewUi
):
    _view  : "DiagramView"
    _scene : "DiagramScene"
