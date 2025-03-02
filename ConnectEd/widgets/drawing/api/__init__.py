"""
API for Drawing widgets.

This module provides the public API for interacting with Drawing widgets,
including view manipulation, element management, and drawing operations.
"""

__all__ = [
    'DrawingApiMixin'
]

from .view  import DrawingApiViewMixin
from .mouse import DrawingApiMouseMixin


class DrawingApiMixin(
    DrawingApiViewMixin,
    DrawingApiMouseMixin
):
    pass
