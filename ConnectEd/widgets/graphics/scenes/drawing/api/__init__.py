from .edit       import DrawingSceneApiEditMixin
from .add        import DrawingSceneApiAddMixin
from .properties import DrawingSceneApiPropertiesMixin


class DrawingSceneApiMixin(
    DrawingSceneApiEditMixin,
    DrawingSceneApiAddMixin,
    DrawingSceneApiPropertiesMixin
):
    pass
