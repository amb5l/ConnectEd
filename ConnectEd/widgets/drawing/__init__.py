"""
Drawing components for the ConnectEd application.

This module provides classes for creating and manipulating drawings,
including the main Drawing widget and DrawingSubWindow container.
"""

__all__ = [
    'Drawing',
    'DrawingSubWindow'
]

from types  import NoneType
from dataclasses import dataclass
from typing import Optional, ClassVar

from PyQt6.QtCore    import Qt, QPointF, QSizeF
from PyQt6.QtWidgets import QWidget, QMdiSubWindow, QMdiArea

from ...core  import TypedList, settings
from .private import DrawingPrivateMixin
from .events  import DrawingEventsMixin
from .api     import DrawingApiMixin

#from ...elements import Rectangle

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
    view_rect        : Optional['Drawing.Rect'] = None
    sel_rect         : Optional['Drawing.Rect'] = None
    zoom             : Optional[float] = None
    pan              : QPointF
    mouse            : 'Drawing.Mouse'
    mouse_press_prev : 'Drawing.Pos'
    state            : 'Drawing.State'

    @dataclass
    class Grid:
        """Grid configuration for the drawing."""
        display : bool
        snap    : bool
        x       : int
        y       : int

    def __init__(
        self: 'Drawing',
        parent: QWidget,
        main_window: 'MainWindow'
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
        # TODO get these from settings
        self.grid = self.Grid(
            display = True,
            snap    = True,
            x       = 10,
            y       = 10
        )
        self.elements         = TypedList(self.ELEMENT_TYPES)
        self.wip              = TypedList(self.ELEMENT_TYPES)
        self.symbols          = None
        self.view_rect        = self.Rect(self, self.visibleRegion().boundingRect())
        self.sel_rect         = self.Rect(self)
        self.grid.display     = settings.prefs.display.grid.display
        self.grid.snap        = settings.prefs.display.grid.snap
        self.grid.x           = settings.prefs.display.grid.x
        self.grid.y           = settings.prefs.display.grid.y
        self.mouse_press_prev = self.Pos()
        self.mouse            = self.Mouse(self)
        self.state            = self.State.Idle
        self.setMouseTracking(True)

        # TODO remove this
        #self.elements.append(Rectangle(QPointF(0, 0), QSizeF(100, 100)))

        self._viewUpdate()

        # uncomment to enable keypress events
        #self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)


class DrawingSubWindow(QMdiSubWindow):
    """A subwindow container for Drawing widgets in the MDI area."""

    def __init__(
        self: 'DrawingSubWindow',
        parent: QMdiArea
    ) -> None:
        """Initialize a DrawingSubWindow.

        Args:
            parent: The parent MDI area
        """
        super().__init__(parent)
