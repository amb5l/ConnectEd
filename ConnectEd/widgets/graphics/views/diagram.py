from typing import Self

from .drawing import DrawingView, DrawingSubWindow

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.diagram import DiagramScene


class DiagramView(DrawingView):
    def viewZoomSheet(self : Self) -> None:
        scene : "DiagramScene" = self.scene()
        rect = scene.sheet.rect
        self._zoomRect(rect)

class DiagramSubWindow(DrawingSubWindow):
    pass
