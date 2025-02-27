from types  import NoneType
from dataclasses import dataclass

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
    ELEMENT_TYPES = TypedList(NoneType)
    main_window : 'MainWindow'  # Use string annotation to avoid circular import
    name        : str
    elements    : TypedList
    wip         : TypedList
    symbols     : TypedList['Symbol']
    sel_prect   : QRect | None = None

    @dataclass
    class Grid:
        display : bool
        snap    : bool
        x       : int
        y       : int

    def __init__(
        self   : 'Drawing',
        parent : QWidget,
        main_window : 'MainWindow'  # Use string annotation to avoid circular import
    ) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.main_window = main_window
        self.zoom = 1.0
        self.pan  = QPointF(0.0, 0.0)
        # TODO get these from settings
        self.grid = self.Grid(
            display = True,
            snap    = True,
            x       = 10,
            y       = 10
        )
        self.elements  = TypedList(self.ELEMENT_TYPES)
        self.wip       = TypedList(self.ELEMENT_TYPES)
        self.symbols   = None
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
    def __init__(
        self    : 'DrawingSubWindow',
        parent  : QMdiArea
    ) -> None:
        super().__init__(parent)
