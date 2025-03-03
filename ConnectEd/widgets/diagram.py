from types import NoneType
from typing import Optional

from PyQt6.QtCore    import QRect, QPoint, QSize
from PyQt6.QtWidgets import QWidget, QMdiArea, QMdiSubWindow

from ..core   import settings, TypedList, PainterContext
from .drawing import Drawing
from .symbol  import Symbol

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import MainWindow


class Diagram(Drawing):
    ELEMENT_TYPES = [NoneType]
    sheet   : Optional[QSize] = None
    border  : Optional[int] = None
    symbols : TypedList[Symbol]

    def __init__(
        self        : 'Drawing',
        parent      : QWidget,
        main_window : 'MainWindow'
    ) -> None:
        super().__init__(parent, main_window)
        self.sheet   = getattr(settings.sheet_sizes, settings.defaults.sheet)
        self.border  = settings.defaults.border
        self.symbols = TypedList[Symbol]()

    def paintSheet(self : 'Diagram', ctx : PainterContext) -> None:
        if self.sheet:
            ctx.setBrush(settings.theme.sheet)
            ctx.painter.fillRect(QRect(QPoint(0, 0), self.sheet), ctx.brush)
            ctx.setPenOnly(
                settings.theme.border,
                settings.prefs.display.border.width,
                settings.prefs.display.border.style
            )
            ctx.painter.drawRect(QRect(
                QPoint(0, 0) + QPoint(self.border, self.border),
                self.sheet - (2 * QSize(self.border, self.border))
            ))

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
