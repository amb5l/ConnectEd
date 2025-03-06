"""
API for Drawing widgets.

This module provides the public API for interacting with Drawing widgets,
including view manipulation, element management, and drawing operations.
"""

__all__ = [
    'DrawingApiMixin'
]

from .view    import DrawingApiViewMixin
from .mouse   import DrawingApiMouseMixin
from .place   import DrawingApiPlaceMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from .. import Drawing


class DrawingApiMixin(
    DrawingApiViewMixin,
    DrawingApiMouseMixin,
    DrawingApiPlaceMixin
):
    def paintSheet(self : 'Drawing') -> None:
        """
        Placeholder to be overridden by Diagram.
        """
        pass
