__all__ = ['DiagramView', 'DiagramSubWindow']

from typing import Optional

from PyQt6.QtWidgets import QMdiArea

from .drawing import DrawingScene, DrawingView, DrawingSubWindow
from ..items  import Paper, Border

from ... import hub

class DiagramView(DrawingView):
    paper   : Paper
    border  : Border

    def __init__(self : 'DrawingView', scene : DrawingScene) -> None:
        super().__init__(scene)
        self.paper   = Paper(hub.settings.defaults.sheet)
        self.border  = Border(self.paper, hub.settings.defaults.margin)
        self.scene().addItem(self.paper)
        self.scene().addItem(self.border)

    def viewZoomSheet(self : 'DiagramView') -> None:
        self._zoomRect(self.sheet.rect)

class DiagramSubWindow(DrawingSubWindow):
    def __init__(
        self   : 'DiagramSubWindow',
        parent : Optional[QMdiArea] = None
    ) -> None:
        if parent is None:
            parent = hub.main_window.mdi_area
        super().__init__(parent)
