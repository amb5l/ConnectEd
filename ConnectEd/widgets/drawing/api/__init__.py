"""
API for Drawing widgets.

This module provides the public API for interacting with Drawing widgets,
including view manipulation, element management, and drawing operations.
"""

__all__ = [
    'DrawingApiMixin'
]

from .view import DrawingApiViewMixin


class DrawingApiMixin(
    DrawingApiViewMixin
):
    pass
