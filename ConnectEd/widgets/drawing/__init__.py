"""
Drawing components for the ConnectEd application.

This module provides classes for creating and manipulating drawings,
including the main Drawing widget and DrawingSubWindow container.
"""

__all__ = [
    'Drawing',
    'DrawingSubWindow'
]

from types       import NoneType
from dataclasses import dataclass
from typing      import Optional, ClassVar

from PyQt6.QtCore    import Qt, QPointF, QPoint
from PyQt6.QtWidgets import QMdiArea, QMdiSubWindow, QWidget

from ...core  import TypedList, settings
from .private import DrawingPrivateMixin
from .events  import DrawingEventsMixin
from .api     import DrawingApiMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING: # avoid circular import issues
    from ..symbol import Symbol
    from ..main_window import MainWindow


class Drawing(
    QWidget,
    DrawingEventsMixin,
    DrawingPrivateMixin,
    DrawingApiMixin
):
    """Main drawing widget for the ConnectEd application.

    This class provides the core drawing functionality, including:
    - Element management (adding, removing, selecting)
    - View manipulation (zooming, panning)
    - Grid display and snapping
    - Event handling (mouse, keyboard, paint)
    """
    ELEMENT_TYPES    : ClassVar[TypedList] = TypedList(NoneType)
    main_window      : 'MainWindow'
    name             : str
    elements         : TypedList
    wip              : TypedList
    symbols          : Optional[TypedList['Symbol']]
    view_rect        : Optional['Drawing.Rect']
    sel_rect         : Optional['Drawing.Rect']
    zoom             : Optional[float]
    pan              : QPointF
    mouse            : 'Drawing.Mouse'
    state            : 'Drawing.State'

    def __init__(
        self        : 'Drawing',
        parent      : QWidget,
        main_window : 'MainWindow'
    ) -> None:
        """Initialize a Drawing widget.

        Args:
            parent: The parent widget
            main_window: The main application window
        """
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.main_window = main_window
        self.zoom = 1.0
        self.pan = QPointF(0.0, 0.0)
        self.elements         = TypedList(self.ELEMENT_TYPES)
        self.wip              = TypedList(self.ELEMENT_TYPES)
        self.symbols          = None
        self.view_rect        = self.PLRect(self, self.visibleRegion().boundingRect())
        self.sel_rect         = None
        self.mouse            = self.Mouse(self)
        self.state            = self.State.Idle
        self.setMouseTracking(True)
        self._viewUpdate()

        # uncomment to enable keypress events
        #self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)


class DrawingSubWindow(QMdiSubWindow):
    """A subwindow container for Drawing widgets in the MDI area."""

    def __init__(
        self   : 'DrawingSubWindow',
        parent : QMdiArea
    ) -> None:
        """Initialize a DrawingSubWindow.

        Args:
            parent: The parent MDI area
        """
        super().__init__(parent)
