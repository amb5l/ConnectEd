__all__ = [
    'Diagram'
]

from PyQt6.QtWidgets import QWidget, QMdiArea

from ..core   import settings, TypedList
from .        import Paper, Border, Symbol, Drawing, DrawingSubWindow

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import MainWindow


class Diagram(Drawing):
    paper   : Paper
    border  : Border
    symbols : TypedList[Symbol]

    def __init__(
        self        : 'Diagram',
        parent      : QWidget,
        main_window : 'MainWindow'
    ) -> None:
        super().__init__(parent, main_window)
        self.paper   = Paper(settings.defaults.sheet)
        self.border  = Border(self.paper, settings.defaults.margin)
        self.symbols = TypedList[Symbol]()
        self.scene.addItem(self.paper)
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
