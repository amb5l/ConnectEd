"""
Event handling for Drawing widgets.

This module provides mixins for handling various events in Drawing widgets,
including paint events, resize events, and user interactions.
"""

__all__ = [
    'DrawingViewEventsMixin'
]

from .mouse import DrawingEventsMouseMixin


class DrawingViewEventsMixin(
    DrawingEventsMouseMixin
):
    pass
