from ...drawing.api import DrawingSceneApiMixin

from .add  import DiagramSceneApiAddMixin
from .conn import DiagramSceneApiConnMixin

class DiagramSceneApiMixin(
    DiagramSceneApiAddMixin,
    DiagramSceneApiConnMixin,
    DrawingSceneApiMixin
):
    pass
