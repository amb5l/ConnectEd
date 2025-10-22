from .edit  import DrawingViewUiEditMixin
from .view  import DrawingViewUiViewMixin
from .place import DrawingViewUiPlaceMixin


class DrawingViewUi(
    DrawingViewUiEditMixin,
    DrawingViewUiViewMixin,
    DrawingViewUiPlaceMixin
):
    pass
