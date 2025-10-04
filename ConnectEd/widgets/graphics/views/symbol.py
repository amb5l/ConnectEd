from typing import Self

from PyQt6.QtCore    import QEvent
from PyQt6.QtWidgets import QMdiArea

from .drawing import DrawingView, DrawingSubWindow


class SymbolView(DrawingView):
    def showEvent(self : Self, event : QEvent) -> None:
        super().showEvent(event)
        self.viewZoomAll()


class SymbolSubWindow(DrawingSubWindow):
    def __init__(
        self   : Self,
        parent : QMdiArea | None = None
    ) -> None:
        super().__init__(parent)
