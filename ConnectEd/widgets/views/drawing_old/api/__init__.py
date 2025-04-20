__all__ = ['DrawingApiMixin']

from .edit    import DrawingApiEditMixin
from .view    import DrawingApiViewMixin
from .mouse   import DrawingApiMouseMixin
from .place   import DrawingApiPlaceMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from .. import DrawingView


class DrawingViewApiMixin(
    DrawingApiEditMixin,
    DrawingApiViewMixin,
    DrawingApiMouseMixin,
    DrawingApiPlaceMixin
):
        pass
