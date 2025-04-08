"""
Event handling for Drawing widgets.

This module provides mixins for handling various events in Drawing widgets,
including paint events, resize events, and user interactions.
"""

__all__ = [
    'DrawingViewEventsMixin'
]

from PyQt6.QtGui import QResizeEvent

from .mouse import DrawingEventsMouseMixin
from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from .. import DrawingView


class DrawingViewEventsMixin(
    DrawingEventsMouseMixin
):
    pass
