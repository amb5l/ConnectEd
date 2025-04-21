__all__ = ["SymbolScene"]

from . import DrawingScene

from ..elements import SymbolInstance, Block


class SymbolScene(DrawingScene):
    FORBIDDEN_ITEMS = [SymbolInstance, Block]
