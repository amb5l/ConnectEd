__all__ = ['DiagramView', 'DiagramSubWindow']

from .drawing   import DrawingView, DrawingSubWindow


class DiagramView(DrawingView):
    def viewZoomSheet(self : 'DiagramView') -> None:
        rect = self.scene().paper_rect()
        self._zoomRect(rect)

class DiagramSubWindow(DrawingSubWindow):
    pass
