__all__ = ["DrawingSceneApiMixin"]

from .file import *
from .place import *

class DrawingSceneApiMixin(
    DrawingSceneApiFileMixin,
    DrawingSceneApiPlaceMixin
):
    pass
