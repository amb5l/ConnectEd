from .edit  import DiagramViewApiEditMixin
from .view  import DiagramViewApiViewMixin
from .place import DiagramViewApiPlaceMixin


class DiagramViewApiMixin(
    DiagramViewApiEditMixin,
    DiagramViewApiViewMixin,
    DiagramViewApiPlaceMixin
):
    pass
