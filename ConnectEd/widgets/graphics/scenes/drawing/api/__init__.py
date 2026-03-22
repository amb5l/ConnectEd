from .edit       import DrawingSceneApiEditMixin
from .add        import DrawingSceneApiAddMixin
from .conn       import DrawingSceneApiConnMixin
from .properties import DrawingSceneApiPropertiesMixin


class DrawingSceneApiMixin(
    DrawingSceneApiEditMixin,
    DrawingSceneApiAddMixin,
    DrawingSceneApiConnMixin,
    DrawingSceneApiPropertiesMixin
):
    pass
