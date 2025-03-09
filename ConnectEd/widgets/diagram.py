from PyQt6.QtWidgets import QWidget, QMdiArea

from ..core     import settings, TypedList
from ..elements import Sheet, Border, Rectangle
from .drawing   import Drawing, DrawingSubWindow
from .symbol    import Symbol

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import MainWindow


class Diagram(Drawing):
    ELEMENT_TYPES = (Sheet, Border, Rectangle)
    border  : Border
    symbols : TypedList[Symbol]

    def __init__(
        self        : 'Diagram',
        parent      : QWidget,
        main_window : 'MainWindow'
    ) -> None:
        super().__init__(parent, main_window)
        self.border  = Border(self.sheet, settings.defaults.margin)
        self.symbols = TypedList[Symbol]()
        self.scene.addItem(self.border)

    def viewZoomSheet(self : 'Diagram') -> None:
        self._zoomRect(self.sheet.rect)

class DiagramSubWindow(DrawingSubWindow):
    """A subwindow container for Diagram drawing widgets in the MDI area."""

    def __init__(
        self   : 'DiagramSubWindow',
        parent : QMdiArea
    ) -> None:
        """Initialize a DiagramSubWindow.

        Args:
            parent: The parent MDI area
        """
        super().__init__(parent)
