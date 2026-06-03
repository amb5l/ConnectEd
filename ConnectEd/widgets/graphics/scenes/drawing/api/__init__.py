from .edit       import DrawingSceneApiEditMixin
from .add        import DrawingSceneApiAddMixin
from .util       import DrawingSceneApiUtilMixin
from .properties import DrawingSceneApiPropertiesMixin


class DrawingSceneApiMixin(
    DrawingSceneApiEditMixin,
    DrawingSceneApiAddMixin,
    DrawingSceneApiUtilMixin,
    DrawingSceneApiPropertiesMixin
):
    pass
