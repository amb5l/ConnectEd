__all__ = ["DrawingSceneApiMixin"]

from .file import *
from .edit import *
from .place import *

class DrawingSceneApiMixin(
    DrawingSceneApiFileMixin,
    DrawingSceneApiEditMixin,
    DrawingSceneApiPlaceMixin
):
    pass
