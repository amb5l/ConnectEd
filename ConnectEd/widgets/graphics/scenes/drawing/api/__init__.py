from .edit import DrawingSceneApiEditMixin
from .add  import DrawingSceneApiAddMixin
from .conn import DrawingSceneApiConnMixin


class DrawingSceneApiMixin(
    DrawingSceneApiEditMixin,
    DrawingSceneApiAddMixin,
    DrawingSceneApiConnMixin
):
    pass
