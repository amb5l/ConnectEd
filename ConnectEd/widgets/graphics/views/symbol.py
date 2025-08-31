from typing import Self, Optional

from PyQt6.QtWidgets import QMdiArea

from .drawing import DrawingView, DrawingSubWindow


class SymbolView(DrawingView):
    pass

class SymbolSubWindow(DrawingSubWindow):
    def __init__(
        self   : Self,
        parent : Optional[QMdiArea] = None
    ) -> None:
        super().__init__(parent)
