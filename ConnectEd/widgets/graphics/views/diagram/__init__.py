from typing import Self

from PyQt6.QtCore import QEvent

from ..drawing import DrawingView, DrawingSubWindow

from .state import DiagramViewStateMixin
from .ui    import DiagramViewUi

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...scenes.diagram import DiagramScene


class DiagramView(DiagramViewStateMixin, DrawingView):
    UI_CLASS = DiagramViewUi

    ui : DiagramViewUi

    def viewZoomSheet(self : Self) -> None:
        scene : "DiagramScene | None" = self.scene()
        if scene is None:
            return
        rect = scene.sheet.rect
        self._zoomRect(rect)

    def showEvent(self : Self, event : QEvent) -> None:
        super().showEvent(event)
        self.viewZoomSheet()


class DiagramSubWindow(DrawingSubWindow):
    pass
