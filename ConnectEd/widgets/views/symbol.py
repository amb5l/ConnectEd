__all__ = ['SymbolView', 'SymbolSubWindow']

from typing import Optional

from PyQt6.QtWidgets import QMdiArea

from .drawing import DrawingView, DrawingSubWindow

from ... import hub

class SymbolView(DrawingView):
    pass

class SymbolSubWindow(DrawingSubWindow):
    def __init__(
        self   : 'SymbolSubWindow',
        parent : Optional[QMdiArea] = None
    ) -> None:
        if parent is None:
            parent = hub.main_window.mdi_area
        super().__init__(parent)
