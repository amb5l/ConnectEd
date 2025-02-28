"""
Event handling for Drawing widgets.

This module provides mixins for handling various events in Drawing widgets,
including paint events, resize events, and user interactions.
"""

__all__ = [
    'DrawingEventsMixin'
]

from PyQt6.QtGui import QResizeEvent

from .paint import DrawingEventsPaintMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from .. import Drawing


class DrawingEventsMixin(DrawingEventsPaintMixin):
    def resizeEvent(self : 'Drawing', event : QResizeEvent):
        if self.zoom is None:
            self.viewZoomFull()
        else:
            self._viewUpdate()
