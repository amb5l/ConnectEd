from types import NoneType
from typing import Optional
from PyQt6.QtCore    import QRect, QPoint
from PyQt6.QtWidgets import QMdiArea, QMdiSubWindow, QWidget

from ..core   import settings, TypedList, PainterContext
from .drawing import Drawing
from .symbol  import Symbol

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import MainWindow


class Diagram(Drawing):
    ELEMENT_TYPES = [NoneType]
    sheet   : Optional[str] = None
    border  : Optional[int] = None
    symbols : TypedList[Symbol]

    def __init__(
        self        : 'Drawing',
        parent      : QWidget,
        main_window : 'MainWindow'
    ) -> None:
        super().__init__(parent, main_window)
        self.sheet = getattr(settings.sheet_sizes, settings.defaults.sheet)

    def paintSheet(self : 'Diagram', ctx : PainterContext) -> None:
        ctx.setBrush(settings.theme.sheet)
        ctx.painter.fillRect(QRect(QPoint(0, 0), self.sheet), ctx.brush)

class DiagramSubWindow(QMdiSubWindow):
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
