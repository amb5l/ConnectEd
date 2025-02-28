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
from typing import Optional, ClassVar, List, Type

from PyQt6.QtCore    import Qt, QPointF, QRect
from PyQt6.QtWidgets import QWidget, QMdiSubWindow, QMdiArea

from ...core       import TypedList, settings
# Remove the circular import
# from ..main_window import MainWindow

from .events  import DrawingEventsMixin
from .private import DrawingPrivateMixin
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

    ELEMENT_TYPES: ClassVar[TypedList] = TypedList(NoneType)
    main_window: 'MainWindow'  # Use string annotation to avoid circular import
    name: str
    elements: TypedList
    wip: TypedList
    symbols: Optional[TypedList['Symbol']]
    sel_prect: Optional[QRect] = None
    zoom: float
    pan: QPointF

    @dataclass
    class Grid:
        """Grid configuration for the drawing."""
        display: bool
        snap: bool
        x: int
        y: int

    def __init__(
        self: 'Drawing',
        parent: QWidget,
        main_window: 'MainWindow'  # Use string annotation to avoid circular import
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
        self.elements = TypedList(self.ELEMENT_TYPES)
        self.wip = TypedList(self.ELEMENT_TYPES)
        self.symbols = None
        self.sel_prect = None

        self.grid.display = settings.prefs.display.grid.display
        self.grid.snap    = settings.prefs.display.grid.snap
        self.grid.x       = settings.prefs.display.grid.x
        self.grid.y       = settings.prefs.display.grid.y

        #self.mouseInit()
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
