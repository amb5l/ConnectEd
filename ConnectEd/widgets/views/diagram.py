__all__ = ['DiagramView', 'DiagramSubWindow']

from PyQt6.QtWidgets import QMdiArea

from ...core  import settings, TypedList
from .drawing import Drawing, DrawingView, DrawingSubWindow
from ..scenes import Symbol
from ..items  import Paper, Border


class DiagramView(DrawingView):
    paper   : Paper
    border  : Border

    def __init__(self : 'DrawingView', scene : Drawing) -> None:
        super().__init__(scene)
        self.paper   = Paper(settings.defaults.sheet)
        self.border  = Border(self.paper, settings.defaults.margin)
        self.scene().addItem(self.paper)
        self.scene().addItem(self.border)

    def viewZoomSheet(self : 'DiagramView') -> None:
        self._zoomRect(self.sheet.rect)

class DiagramSubWindow(DrawingSubWindow):
    def __init__(
        self   : 'DiagramSubWindow',
        parent : QMdiArea
    ) -> None:
        super().__init__(parent)
