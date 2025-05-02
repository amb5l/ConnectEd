__all__ = ["DiagramView", "DiagramSubWindow"]

from typing import Self

from .drawing import DrawingView, DrawingSubWindow


class DiagramView(DrawingView):
    def viewZoomSheet(self : Self) -> None:
        rect = self.scene().paper_rect()
        self._zoomRect(rect)

class DiagramSubWindow(DrawingSubWindow):
    pass
