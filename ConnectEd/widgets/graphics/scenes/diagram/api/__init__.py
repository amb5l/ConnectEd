from ...drawing.api import DrawingSceneApiMixin

from .add  import DiagramSceneApiAddMixin
from .conn import DiagramSceneApiConnMixin
from .edit import DiagramSceneApiEditMixin
from .test import DiagramSceneApiTestMixin

class DiagramSceneApiMixin(
    DiagramSceneApiAddMixin,
    DiagramSceneApiConnMixin,
    DiagramSceneApiEditMixin,
    DiagramSceneApiTestMixin,
    DrawingSceneApiMixin
):
    pass
