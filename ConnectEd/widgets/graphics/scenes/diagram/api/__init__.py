from ...drawing.api import DrawingSceneApiMixin

from .add  import DiagramSceneApiAddMixin
from .conn import DiagramSceneApiConnMixin
from .edit import DiagramSceneApiEditMixin

class DiagramSceneApiMixin(
    DiagramSceneApiAddMixin,
    DiagramSceneApiConnMixin,
    DiagramSceneApiEditMixin,
    DrawingSceneApiMixin
):
    pass
