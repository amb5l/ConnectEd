from .edit  import DrawingViewApiEditMixin
from .view  import DrawingViewApiViewMixin
from .place import DrawingViewApiPlaceMixin


class DrawingViewApiMixin(
    DrawingViewApiEditMixin,
    DrawingViewApiViewMixin,
    DrawingViewApiPlaceMixin
):
    pass
